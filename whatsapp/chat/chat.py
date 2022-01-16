import socketio

sio = socketio.Server(cross_allow_origin='*')


# @sio.event
# def connect(sid):
#     pass

# @sio.event
# def disconnect(sid):
#     pass