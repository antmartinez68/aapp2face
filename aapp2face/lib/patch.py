"""
Parche librería zeep para solucionar problema verificación respuesta
"""

from datetime import datetime, timedelta

from zeep.wsse import utils
from zeep.wsse.signature import BinarySignature


class BinarySignatureTimestamp(BinarySignature):
    def apply(self, envelope, headers):
        security = utils.get_security_header(envelope)

        created = datetime.utcnow()
        expired = created + timedelta(seconds=1 * 60)

        timestamp = utils.WSU("Timestamp")
        timestamp.append(
            utils.WSU("Created", created.replace(microsecond=0).isoformat() + "Z")
        )
        timestamp.append(
            utils.WSU("Expires", expired.replace(microsecond=0).isoformat() + "Z")
        )

        security.append(timestamp)

        super().apply(envelope, headers)
        return envelope, headers

    def verify(self, envelope):
        return envelope
