import logging

from OpenSSL import crypto

from lambdas import cfnresponse

key = crypto.PKey()
log = logging.getLogger()

def generate_key():
    log.info("Generating Key")
    key.generate_key(crypto.TYPE_RSA, 2048)
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf-8')


def generate_csr():
    log.info("Generating CSR")
    req = crypto.X509Req()
    req.get_subject().countryName = 'US'
    req.set_pubkey(key)
    req.sign(key, "sha256")
    return crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode('utf-8')


def lambda_handler(event, context):
    try:
        private_key = generate_key()
        csr = generate_csr()
    except Exception as e:
        log.exception(e)
        cfnresponse.send(
            event=event,
            context=context,
            response_status=cfnresponse.FAILED,
            reason=str(e)
        )
        return False
    data = {
        'PrivateKey': private_key,
        'Csr': csr
    }
    cfnresponse.send(
        event=event,
        context=context,
        response_status=cfnresponse.SUCCESS,
        response_data=data
    )
