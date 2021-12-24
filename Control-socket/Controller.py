class Controller(object):
    def get_msg(self, request_params_tuple):
        result_data = "func->get_msg : get it :" + str(request_params_tuple)
        return result_data
