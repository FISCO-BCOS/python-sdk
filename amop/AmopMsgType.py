""" Message types send from fisco bcos node. """
class AmopMsgType :

    """
     * Message types which Client module interested in. CHANNEL_RPC_REQUEST: type of rpc request
     * message TRANSACTION_NOTIFY: type of transaction notify message BLOCK_NOTIFY: type of block
     * notify message
     """
    CHANNEL_RPC_REQUEST=0x12
    TRANSACTION_NOTIFY=0x1000
    BLOCK_NOTIFY=0x1001

    """
     * Message types processed by Client module. CLIENT_HEARTBEAT:type of heart beat message
     * CLIENT_HANDSHAKE:type of hand shake message
     """
    CLIENT_HEARTBEAT=0x13
    CLIENT_HANDSHAKE=0x14

    """
     * Message types processed by EventSubscribe module CLIENT_REGISTER_EVENT_LOG:type of event log
     * filter register request and response message EVENT_LOG_PUSH:type of event log push message
     """
    CLIENT_REGISTER_EVENT_LOG=0x15
    CLIENT_UNREGISTER_EVENT_LOG=0x16
    EVENT_LOG_PUSH=0x1002

    """
     * Message types processed by AMOP module AMOP_REQUEST:type of request message from sdk
     * AMOP_RESPONSE:type of response message to sdk AMOP_MULBROADCAST:type of mult broadcast
     * message AMOP_CLIENT_TOPICS:type of topic request message REQUEST_TOPICCERT:type of request
     * verify message UPDATE_TOPIICSTATUS:type of update status message
     """
    AMOP_REQUEST=0x30
    AMOP_RESPONSE=0x31
    AMOP_MULBROADCAST=0x35
    AMOP_CLIENT_TOPICS=0x32
    REQUEST_TOPICCERT=0x37
    UPDATE_TOPIICSTATUS=0x38
