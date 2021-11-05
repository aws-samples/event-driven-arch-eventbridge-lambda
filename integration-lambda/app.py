import json
import boto3
import xml.etree.ElementTree as ET
import time
import os
import urllib3

def lambda_handler(event, context):

    _integracao_ip = os.environ.get('INTEGRACAO_IP', '0.0.0.0') #IP do simulador
    _integracao_porta = os.environ.get('INTEGRACAO_PORTA', 8080) #POrta do simulador
    _service_url = 'http://{ip}:{porta}/poc/leitura'.format(ip=_integracao_ip, porta=_integracao_porta) #servico de mock q valida os arquivos
    _bucket_leitura = os.environ.get('BUCKET_LEITURAS', 'leituras') #bucket de origem
    _bucket_leitura_correta = os.environ.get('BUCKET_LEITURAS_CORRETAS', 'leituras-corretas') #bucket onde vao os arquivos processados com sucesso
    _bucket_leitura_incorreta = os.environ.get('BUCKET_LEITURAS_INCORRETAS', 'leituras-incorretas') #nome do bucket onde vao os arquivos com erro
    _codigo_retorno_ok = 0 #codigo de retorno ok

    #extraindo dados do bucket/arquivo que trigaram a funcao
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key_name = event['Records'][0]['s3']['object']['key']

    #apenas um debug
    print("Input", event)
    print("Bucket:", bucket_name)
    print("Object:", key_name)

    s3 = boto3.resource('s3')

    #extrai o conteudo do arquivo enviado para uma string
    xmlContent = s3.Object(bucket_name, key_name).get()['Body'].read()

    #define os headers que serao enviados para o servidor de validacao/mock
    headers = {'Content-Type': 'application/xml'}

    #faz o request para o servidor de validacao e captura o retorno
    http = urllib3.PoolManager()
    r = http.request('POST', _service_url,
                 headers=headers,
                 body=xmlContent)
    xmlRetorno = r.data.decode('utf-8')

    #o codigo de retorno fica no meio do arquivo xml(xMotivo)
    # então aqui fazemos o parse do xml e extraimos o campo desejado 
    codigoRetorno = int(ET.fromstring(xmlRetorno).findall('.//codMotivo')[0].text)
    print("Codigo retorno: ", codigoRetorno)

    #move o arquivo para o bucket de acordo com o codigo de retorno
    if codigoRetorno == _codigo_retorno_ok:
        move_file(key_name, _bucket_leitura, _bucket_leitura_correta)
    else:
        move_file(key_name, _bucket_leitura, _bucket_leitura_incorreta)

    return {
        # "statusCode": 200 if codigoRetorno == 103 else 400,
        "body": json.dumps({
            "message": xmlRetorno
        }),
    }

#move o arquivo para o bucket de destino, e exclui o mesmo do bucket de origem
def move_file(key, source_bucket, destination_bucket):
    s3 = boto3.resource('s3')
    copy_source = {
        'Bucket': source_bucket,
        'Key': key
    }
    #gera um arquivo com o nome timestamp-nome para ser enviado
    destination_key = '{ts}-{key}'.format(ts = time.strftime("%Y%m%d%H%M%S"), key=key)
    #copia o arquivo pro bucket de destino
    s3.meta.client.copy(copy_source, destination_bucket, destination_key)
    #apaga da origem
    s3.Object(source_bucket, key).delete()