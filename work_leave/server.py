import grpc
from concurrent import futures
import time

# import the generated classes
import work_leave_pb2
import work_leave_pb2_grpc

class WorkLeaveServicer(work_leave_pb2_grpc.EmployeeLeaveDaysServiceServicer):

    def EligibleForLeave(self, request, context):
        response = work_leave_pb2.LeaveEligibility()
        response.eligible = False
        response.name = request.name
        if (request.requested_leave_days > 0):
            if (request.accrued_leave_days > request.requested_leave_days):
                response.eligible = True
        return response

    def grantLeave(self, request, context):
        granted_leave_days = request.requested_leave_days
        accrued_leave_days = request.accrued_leave_days - granted_leave_days

        response = work_leave_pb2.LeaveFeedback()
        response.granted = True
        response.name = request.name
        response.accrued_leave_days = accrued_leave_days
        response.granted_leave_days = granted_leave_days
        return response

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

work_leave_pb2_grpc.add_EmployeeLeaveDaysServiceServicer_to_server(
    WorkLeaveServicer(), server)

# listen on port 50051
print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
