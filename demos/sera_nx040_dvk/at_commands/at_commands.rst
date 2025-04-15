##########################
NX040 AT Command Reference
##########################

This document describes the AT commands supported by the Ezurio Sera NX040
module. The NX040 module is a Bluetooth Low Energy (BLE) and Ultrawide Band
(UWB) module. There are AT commands to control the BLE and UWB functionality
of the module.

**************************
Module Management Commands
**************************

ATE
===
Command
    | ``ATEn``

Description
    This command is used to enable or disable command echo. The ``n`` is the
    echo mode. A value of ``0`` disables echo. A value of ``1`` enables echo.
    The default value is ``1``.

Possible Responses
    | ``OK``
    | ``ERROR``

ATI
===
Command
    | ``ATIn``

Description
    Queries read-only parameter data identified by the integer argument ``n``. Values
    returned are either integer or string data sent on a new line before the ``OK``
    response.

    The following information is returned with identifier ``n``:

+------+------------------------------------------------------------+
| ID   | Description                                                |
+======+============================================================+
| 0    | Module name                                                |
+------+------------------------------------------------------------+
| 3    | Firmware version                                           |
+------+------------------------------------------------------------+
| 4    | BLE Address                                                |
+------+------------------------------------------------------------+
| 5    | Unique device identifier                                   |
+------+------------------------------------------------------------+
| 2001 | Last reset reason                                          |
+------+------------------------------------------------------------+
| 2002 | Free memory                                                |
+------+------------------------------------------------------------+
| 2003 | Allocated memory                                           |
+------+------------------------------------------------------------+

Possible Responses
    | ``OK``
    | ``ERROR``

ATZ
===
Command
    | ``ATZ``

Description
    This command is used to reset the module. The reset is equivalent to a
    power cycle.

Possible Responses
    This command has no response, but the module will reset and issue an ``OK``
    response when it is ready to accept commands.

************
UWB Commands
************

AT+UWBS
=======
Command
    | ``AT+UWBSn, role <, type <, preamble <, channel>>>``

Description
    This commmand is used to create a new UWB session. The ``n`` is the session
    identifier. The session identifier is used to identify the session in future
    commands and responses. The session identifier is shared between the device
    and remote peers. The ``role`` is the role of the device in the session. The
    value ``0`` indicates that the device is an initiator/controller. The value
    ``1`` indicates that the device is a responder/controllee. The ``type`` is
    ``0`` for a unicast session and ``1`` for a multicast session. The ``preamble``
    is the preamble code index value to use for the session (9-12). The ``channel``
    is the channel number to use for the session (1-9).

    ``type`` is optional and defaults to ``0``. ``preamble`` is optional and
    defaults to ``9``. ``channel`` is optional and defaults to ``9``.

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSD
========
Command
    | ``AT+UWBSDn``

Description
    This command is used to delete a UWB session. The ``n`` is the session
    identifier.

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSA
========
Command
    | ``AT+UWBSAn, local, remote``

Description
    This command is used to set the local and remote addresses to be used for
    a UWB session. The ``n`` is the session identifier. The ``local`` and
    ``remote`` are the addresses of the local and remote devices. The addresses
    are 16-bit values. For a multicast session, the initial peer/remote address
    should be specified here and additional peers should be added using the
    ``AT+UWBSAM`` command.

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSAM
=========
Command
    | ``AT+UWBSAMn, remote``

Description
    This command is used to add a peer to a multicast UWB session. The ``n`` is
    the session identifier. The ``remote`` is the address of the peer to add.
    Peers can be removed from the session using the ``AT+UWBSAMX`` command.

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSAMX
==========
Command
    | ``AT+UWBSAMXn, remote``

Description
    This command is used to remove a peer from a multicast UWB session. The ``n``
    is the session identifier. The ``remote`` is the address of the peer to remove.

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSI
========
Command
    | ``AT+UWBSIn, interval``

Description
    This command is used to set the ranging interval for a UWB session. The ``n``
    is the session identifier. The ``interval`` is the time in milliseconds between
    ranging attempts. The value must be between 100 and 5000. The interval should
    match on both ends of the ranging session.

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSC
========
Command
    | ``AT+UWBSCn, cfg, value``

Description
    This command is used to set session configuration parameters. The ``n`` is
    the session identifier. The ``cfg`` is the configuration parameter to set.
    The ``value`` is the value to which to set the parameter. The value is expected
    to be a string of hex digits (e.g., ``1234ABCD``).

Possible Responses
    | ``OK``
    | ``ERROR``

AT+UWBSS
========
Command
    | ``AT+UWBSSn``

Description
    This command is used to start a UWB session. The ``n`` is the session
    identifier. Ranging responses will be sent to the host when the session
    is started. The ``AT+USBSA`` command must be used to set the local and remote
    addresses before starting the session.

Possible Responses
    | ``OK``
    | ``ERROR``

*********
Responses
*********

RANGE
=====
Response
    | ``RANGE:n addr range``

Description
    This response is sent when a range measurement is completed. The ``n`` is
    the UWB session identifer. The ``addr`` is the address of the device that
    was ranged. The ``range`` is the distance in centimeters to the device.
    If the ranging failed, the ``range`` value will be 65535.
