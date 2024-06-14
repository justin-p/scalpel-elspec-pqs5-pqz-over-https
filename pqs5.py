"""
Elspec PQS5 endpoint (PQZ over HTTPS) protocol scalpel thingamajig.
"""

import binascii
from base64 import b64decode, b64encode

import xmltodict
from pyscalpel import Request, Response


def keys_exists(element, *keys):
    """
    Check if *keys (nested) exists in `element` (dict).
    """
    if not isinstance(element, dict):
        raise AttributeError("keys_exists() expects dict as first argument.")
    if len(keys) == 0:
        raise AttributeError("keys_exists() expects at least two arguments, one given.")

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


def req_edit_in(req: Request) -> bytes:
    """
    incoming HTTP request
    """
    if req.content:
        try:
            soap = xmltodict.parse(req.content)
            if keys_exists(soap, "s:Envelope", "s:Body", "RequestBinary", "request"):
                base = soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"]
                plain = b64decode(base, validate=True)
                soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"] = str(plain)

            elif keys_exists(
                soap, "s:Envelope", "s:Body", "TaskRequestBinary", "request"
            ):
                base = soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"]
                plain = b64decode(base, validate=True)
                soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"] = str(
                    plain
                )

            elif keys_exists(soap, "s:Envelope", "s:Body", "IdentifyRequestXML"):
                pass
            debug = True
            if debug:
                open = str(plain).strip("b'").split("<")[0]
                sid_k = str(plain).strip("b'").split("<")[1].split(":")[0]
                sid_v = str(plain).strip("b'").split("<")[1].split(":")[1].strip(">")
                rid_k = str(plain).strip("b'").split(">")[1].split("<")[1].split(":")[0]
                rid_v = str(plain).strip("b'").split(">")[1].split("<")[1].split(":")[1]
                PQZ = (
                    str(plain)
                    .strip("b'")
                    .split(">")[2]
                    .split(":")[1]
                    .split("PQZS")[1]
                    .split("\\x02")
                )
                PQZ = "\n".join("".join(PQZ).split("\\x00"))
                req.content = f"""{open}
{sid_k} : {sid_v}
{rid_k} : {rid_v}
PQZ Start

{PQZ}

PQZ End
"""
            else:
                req.content = xmltodict.unparse(soap)
        except binascii.Error:
            pass

        return req.content


def req_edit_out(req: Request, text: bytes) -> Request:
    """
    outgoing HTTP request
    """
    if req.content:
        try:
            soap = xmltodict.parse(text)

            if keys_exists(soap, "s:Envelope", "s:Body", "RequestBinary", "request"):
                plain = soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"]
                base = b64encode(plain, validate=True)
                soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"] = str(base)

            elif keys_exists(
                soap, "s:Envelope", "s:Body", "TaskRequestBinary", "request"
            ):
                plain = soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"]
                base = b64encode(plain, validate=True)
                soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"] = str(base)

            elif keys_exists(soap, "s:Envelope", "s:Body", "IdentifyRequestXML"):
                pass

            req.content = xmltodict.unparse(soap)
        except binascii.Error:
            pass

    return bytes(req)


def res_edit_in(res: Response) -> bytes:
    """
    incoming HTTP response
    """
    if res.content:
        try:
            soap = xmltodict.parse(res.content)
            if keys_exists(
                soap,
                "s:Envelope",
                "s:Body",
                "RequestBinaryResponse",
                "RequestBinaryResult",
            ):
                base = soap["s:Envelope"]["s:Body"]["RequestBinaryResponse"][
                    "RequestBinaryResult"
                ]
                plain = b64decode(base, validate=True)
                soap["s:Envelope"]["s:Body"]["RequestBinaryResponse"][
                    "RequestBinaryResult"
                ] = str(plain)

            elif keys_exists(
                soap,
                "s:Envelope",
                "s:Body",
                "TaskRequestBinaryResponse",
                "TaskRequestBinaryResult",
            ):
                base = soap["s:Envelope"]["s:Body"]["TaskRequestBinaryResponse"][
                    "TaskRequestBinaryResult"
                ]
                plain = b64decode(base, validate=True)
                soap["s:Envelope"]["s:Body"]["TaskRequestBinaryResponse"][
                    "TaskRequestBinaryResult"
                ] = str(plain)

            elif keys_exists(
                soap,
                "s:Envelope",
                "s:Body",
                "IdentifyRequestXMLResponse",
                "IdentifyRequestXMLResult",
            ):
                pass

            debug = True
            if debug:
                open = str(plain).strip("b'").split("<")[0]
                rid_k = str(plain).strip("b'").split("<")[1].split(":")[0]
                rid_v = str(plain).strip("b'").split("<")[1].split(":")[1]
                PQZ = (
                    str(plain)
                    .strip("b'")
                    .split("<")[1]
                    .split(":")[2]
                    .split("PQZS")[1]
                    .split("\\x02")
                )
                PQZ = "\n".join("".join(PQZ).split("\\x00"))
                res.content = bytes(
                    f"""{open}
{rid_k} : {rid_v}
PQZ Start

{PQZ}

PQZ End
""",
                    encoding="UTF8",
                )
            else:
                res.content = bytes(xmltodict.unparse(soap), encoding="utf8")
        except binascii.Error:
            pass

    return res.content


def res_edit_out(res: Response, text: bytes) -> Response:
    """
    outgoing HTTP response.
    """
    if res.content:
        try:
            soap = xmltodict.parse(text)

            if keys_exists(soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"]):
                plain = soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"]
                base = b64encode(plain, validate=True)
                soap["s:Envelope"]["s:Body"]["RequestBinary"]["request"] = str(base)

            elif keys_exists(
                soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"]
            ):
                plain = soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"]
                base = b64encode(plain, validate=True)
                soap["s:Envelope"]["s:Body"]["TaskRequestBinary"]["request"] = str(base)

            elif keys_exists(
                soap,
                "s:Envelope",
                "s:Body",
                "IdentifyRequestXMLResponse",
                "IdentifyRequestXMLResult",
            ):
                pass

            res.content = xmltodict.unparse(soap)
        except binascii.Error:
            pass

    return res
