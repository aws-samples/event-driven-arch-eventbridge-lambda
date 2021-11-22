package main

import (
	"encoding/xml"
	"fmt"
	"net/http"
	"os"
	"time"
)

//to test
// curl -i -X POST -H "Content-Type: multipart/form-data" -F "data=@teste.xml" http://localhost:3000/

type NF struct {
	XMLName             xml.Name          `xml:"nf"`
	TipoAmbiente        string            `xml:"tpAmb"`
	TipoTransmissao     string            `xml:"tpTransm"`
	DataHoraTransmissao time.Time         `xml:"dhTransm"`
	InformacaoLeitura   InformacaoLeitura `xml:"infLeitura"`
}

type InformacaoLeitura struct {
	UF                string  `xml:"cUF"`
	CnpjOperador      string  `xml:"CNPJOper"`
	CodigoEquipamento string  `xml:"cEQP"`
	Latitude          float64 `xml:"latitude"`
	Longitude         float64 `xml:"longitude"`
	TipoSentido       string  `xml:"tpSentido"`
	Placa             string  `xml:"placa"`
	TipoVeiculo       string  `xml:"tpVeiculo"`
	Velocidade        int     `xml:"velocidade"`
	Foto              string  `xml:"foto"`
	IndiceConfianca   int     `xml:"indiceConfianca"`
	PesoBrutoTotal    int     `xml:"pesoBrutoTotal"`
	NumeroEixos       int     `xml:"nrEixos"`
}

type Retorno struct {
	XMLName          xml.Name  `xml:"recepcaoLeitura"`
	TipoAmbiente     int       `xml:"tpAmb"`
	VersaoAplicacao  int       `xml:"verApl"`
	DataHoraResposta time.Time `xml:"dhResp"`
	CodigoMotivo     int       `xml:"codMotivo"`
	DescricaoMotivo  string    `xml:"descMotivo"`
}

func ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Println(r.RequestURI)
	switch {
	case r.Method == http.MethodPost && r.RequestURI == "/poc/leitura":
		CheckDadosNF(w, r)
		return
	case r.Method == http.MethodGet && r.RequestURI == "/poc/gerarArquivos":
		gerarMassaTeste(100, "valido")
		gerarMassaTeste(100, "invalido")
		return
	default:
		return
	}
}

func main() {
	http.HandleFunc("/", ServeHTTP)
	http.ListenAndServe(":8080", nil)
}

func CheckDadosNF(w http.ResponseWriter, r *http.Request) {
	var nf NF
	if err := xml.NewDecoder(r.Body).Decode(&nf); err != nil {
		fmt.Printf("%s", err)
		internalServerError(w, r)
		return
	}

	var codigoErro int = 0
	var descricaoErro string
	if nf.InformacaoLeitura.IndiceConfianca < 90 {
		codigoErro = 100
		descricaoErro = "Indice de confianca abaixo do esperado"
	}

	if len(nf.InformacaoLeitura.Placa) != 7 {
		codigoErro = 200
		descricaoErro = "Placa invalida"
	}

	xmlRetorno, err := xml.Marshal(geraRetorno(codigoErro, descricaoErro))
	if err != nil {
		internalServerError(w, r)
		return
	}

	if codigoErro > 0 {
		w.WriteHeader(http.StatusInternalServerError)
	} else {
		w.WriteHeader(http.StatusOK)
	}
	w.Header().Set("content-type", "application/xml")
	w.Write([]byte(xmlRetorno))
}

func geraRetorno(CodigoErro int, Descricao string) Retorno {
	var now = time.Now().Format(time.RFC3339)
	t, _ := time.Parse(time.RFC3339, now)

	var retorno Retorno
	retorno.TipoAmbiente = 2
	retorno.VersaoAplicacao = 2
	retorno.DataHoraResposta = t
	retorno.CodigoMotivo = CodigoErro
	retorno.DescricaoMotivo = Descricao

	return retorno
}

func gerarMassaTeste(quantidade int64, filename string) {
	var path string = "test/"
	var sourceFile string = fmt.Sprintf("%s%s%s", path, filename, ".xml")
	fmt.Printf("%s", sourceFile)
	for i := 0; i < int(quantidade); i++ {
		var destinationFile string = fmt.Sprintf("%s%s-%d%s", path, filename, i, ".xml")
		copyFile(sourceFile, destinationFile)
	}
}

func s3Upload() {

}

func copyFile(in, out string) (int64, error) {
	i, e := os.Open(in)
	if e != nil {
		fmt.Println(e)
		return 0, e
	}
	defer i.Close()
	o, e := os.Create(out)
	if e != nil {
		return 0, e
	}
	defer o.Close()
	return o.ReadFrom(i)
}

func internalServerError(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusInternalServerError)
	w.Write([]byte("internal server error"))
}
