from .views import get_distributor_name  # Ensure the function is accessible

class UserParameterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # Store the next middleware/view to call

    def __call__(self, request):
        # Attach session parameters to the request
        request.user_param1 = request.session.get('param1', None)
        request.user_param2 = request.session.get('param2', None)
        #print(request.user_param2)
        # Check if param1 has changed or is new
        if request.user_param1:
            # Fetch distributor name based on param1
            current_param3 = request.session.get('param3', None)
            new_param3 = get_distributor_name(request.user_param1)

            if request.user_param2=='Distributor':
                # Update param3 if it has changed
                if current_param3 != new_param3:
                    request.session['param3'] = new_param3
            if request.user_param2=='Ramraj':
                    request.session['param3'] = 'Ramraj'                    

        # Call the next middleware or view
        response = self.get_response(request)
        return response
