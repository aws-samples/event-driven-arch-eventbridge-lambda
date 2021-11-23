package main

import (
	"context"
	"encoding/xml"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
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
	fmt.Println("Request feito para a URI ", r.RequestURI)
	switch {
	case r.Method == http.MethodPost && r.RequestURI == "/poc/leitura":
		CheckDadosNF(w, r)
		return
	case r.Method == http.MethodGet && r.RequestURI == "/poc/gerarArquivos":
		// make async calls to method and return a success code to user
		w.WriteHeader(http.StatusCreated)
		go gerarMassaTeste(100, "valido")
		go gerarMassaTeste(100, "invalido")
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
	fmt.Println("Inicio - geração da massa de testes")
	var testFilePath string = "test/"
	var sourceFile string = fmt.Sprintf("%s%s%s", testFilePath, filename, ".xml")
	var destinationBucket string = getEnv("SIMULADOR_BUCKET_ENTRADA", "upload-test-22112021")
	fmt.Println("Bucket de entrada: ", destinationBucket)

	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		fmt.Println("Failed to load configuration: ", err)
	}
	fmt.Println("Iniciando client s3")
	client := s3.NewFromConfig(cfg)

	for i := 0; i < int(quantidade); i++ {
		fmt.Println("Abrindo arquivo modelo")
		fileToUpload, err := os.Open(sourceFile)
		if err != nil {
			fmt.Println("Unable to open file ", fileToUpload)
			return
		}
		defer fileToUpload.Close()
		var key string = fmt.Sprintf("%s-%d%d%s", filename, time.Now().UnixMicro(), i, ".xml")
		fmt.Println("Enviando arquivo para S3: ", key)
		returnFromS3, err := client.PutObject(context.TODO(), &s3.PutObjectInput{
			Bucket: aws.String(destinationBucket),
			Key:    aws.String(key),
			Body:   fileToUpload,
		})
		fmt.Println("retorno s3: ", returnFromS3)

		if err != nil {
			fmt.Println("Failed to upload file: ", err)
		}
	}
	fmt.Println("Fim - geração da massa de testes")
}

// getEnv get key environment variable if exist otherwise return defalutValue
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return defaultValue
	}
	return value
}

func internalServerError(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusInternalServerError)
	w.Write([]byte("internal server error"))
}
