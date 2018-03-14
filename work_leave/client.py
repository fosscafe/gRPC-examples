import grpc

import work_leave_pb2
import work_leave_pb2_grpc

def main():
    """Python Client for Employee leave days"""

    # Create channel and stub to server's address and port.
    channel = grpc.insecure_channel('localhost:50051')
    stub = work_leave_pb2_grpc.EmployeeLeaveDaysServiceStub(channel)

    user1 = work_leave_pb2.Employee(employee_id = 1,
                                    name = 'Enrico Fermi',
                                    accrued_leave_days = 10,
                                    requested_leave_days = 4)
    user2 = work_leave_pb2.Employee(employee_id = 2,
                                    name = 'Heisenberg',
                                    accrued_leave_days = 10,
                                    requested_leave_days = 20)
    user3 = work_leave_pb2.Employee(employee_id = 3,
                                    name = 'Tesla',
                                    accrued_leave_days = 10,
                                    requested_leave_days = -1)
    user4 = work_leave_pb2.Employee(employee_id = 4,
                                    name = 'Elon Musk',
                                    accrued_leave_days = 10,
                                    requested_leave_days = 5)
    users = [user1, user2, user3, user4]

    for user in users:
        try:
            # Check if the Employee is eligible or not.
            response = stub.EligibleForLeave(user)
            if (not response.eligible):
                print(response.name, "is not eligible")
            else:
                print(response.name, "is eligible")

            # If the Employee is eligible, grant them leave days.
            if response.eligible:
                leaveRequest = stub.grantLeave(user)
                print(leaveRequest)
            print('\n')
        # Catch any raised errors by grpc.
        except grpc.RpcError as e:
            print("Error raised: " + e.details())

if __name__ == '__main__':
    main()
