
import requests
import json
import pprint
import inspect
import re


"""
TODO:
some renaming

GET should usually be URL params, return JSON or text
POST should usually be form params or JSON, depending and return JSON
PUT should be the same as POST
DELETE doesn't have any parameters and doesn't return anything other than a status code

input types: URL_ONLY/URL_PARAMS, FORM_PARAMS, BODY_JSON
output types: status code only, text, json

METHOD    INPUT_TYPE    OUTPUT_TYPE
GET       
POST
PUT
DELETE
"""


def print_debug(response):
    
    print "++++++++++++++++++++++++++++++++++++++++++"
    request = response.request
    
    print request
    print request.url
    print request.headers
    #print request.params
    print request.body
    print "==============================="
    print response
    print response.headers
    print response.text
    print
    print "---------------------------------------"
    
def snake2camel(name):
    return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), name)
    
def camel2snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def http_success(response):
    return response.status_code >= 200 and response.status_code <= 299

def camelify_kwargs(kwargs_dict):
    
    for key, value in kwargs_dict.iteritems():
        cameled_key = snake2camel(key)
        if cameled_key != key:
            del kwargs_dict[key]
            kwargs_dict[cameled_key] = value
            
    return kwargs_dict

def promote_params(kwargs_dict):
    if "params" in kwargs_dict:
        params = kwargs_dict["params"]
        del kwargs_dict["params"]
        kwargs_dict.update(params)
    
    return kwargs_dict

def get_headers(kwargs_dict):
    pass
    
def parse_response(response):
    """
    This is the best place to do debugging since you've got the request AND the response
    """
    request = response.request
    
    #print_debug(response)
    
    #if False:
    if http_success(response):
        #print [response.text, ]
        result = json.loads(response.text)
    else:
        #print response.text
        print "GOT AN EXCEPTION!!!!"
        print_debug(response)
        raise Exception("Problem parsing %s with body %s: %s" % (request.url, request.body, response))
        
    return result

def dictize_list(key_name, value_list):
    dict_list = []
    for value in value_list:
        dict_list.append({key_name: value})
    return dict_list




class EMConnector(object):
    """
    Instantiate one of these and get easy Enterprise Manager API calls
    """
    host = None
    port = None
    user = None
    password = None
    analysis_server = None
    version = None
    debug = None
    timeout = None
    

    def __init__(self, host="localhost", port="8080", user="admin", password="adminadmin", analysis_server=1, version=None, debug=False, timeout=None):
    #def __init__(em_host="localhost", em_port="8080", em_user="admin", em_password="adminadmin"):
    #def __init__(self, debug_level=None, logfile=None, em_host="localhost", em_port="8080", em_user="admin", em_password="adminadmin")
    #    super(EMConnector, self).__init__(debug_level, logfile)
        
        #self.set_values(*args, **kwargs)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.analysis_server = analysis_server
        self.version = version
        
        if version:
            self.url_root = "api/v%s/" % ( self.version)
        else:
            self.url_root = "api/"
            
        #this doesn't do anything yet!
        self.debug = debug
        
        #this does do things
        self.timeout = timeout
        
    """
    def set_em_values(self, *args, **kwargs):
        self.em_host = kwargs.get("em_host", "localhost")
        self.em_port = kwargs.get("em_port", "8080")
        self.em_user = kwargs.get("em_user", "admin")
        self.em_password = kwargs.get("em_password", "adminadmin")
    """
    
    def build_url(self, url_fragment):
        
        url = self.url_root + url_fragment
        full_url = "http://%s:%s/%s" % (str(self.host), str(self.port), str(url))
        #print full_url
        return full_url
    
    def add_default(self, params):
        if params:
            params["maxResults"] = params.get("maxResults", 1000)
            params["analysis_server"] = params.get("analysis_server", self.analysis_server)
        else:
            params = {"maxResults": 1000, "analysis_server": self.analysis_server }
            
        return params
        
    
    def get2text(self, url_fragment, params=None, json=None, headers=None):
        
        #headers = {"Accept": "application/text"}
        params = self.add_default(params)
            
        response = requests.get(self.build_url(url_fragment), auth=(self.user, self.password),  params=params, json=json, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text
    
    #it seems like maybe this only works for POST/PUT
    def get2json(self, url_fragment, params=None, json=None, headers=None):
    #def get2json(self, url_fragment, params=None, headers=None):
        if not headers:
            headers = {"Accept": "application/json"}
            
        params = self.add_default(params)
        
        response = requests.get(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers, timeout=self.timeout)
        #response = requests.get(self.build_url(url_fragment), auth=(self.user, self.password), params=params, headers=headers)
        response.raise_for_status()
        return parse_response(response)
    
    def post2code(self, url_fragment, params=None, json=None, headers=None):
        #response = requests.post(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers)
        #params["analysis_server"] = params.get("analysis_server", self.analysis_server)
        
        response = requests.post(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers, timeout=self.timeout)
        #response.raise_for_status()
        return http_success(response)
    
    def post2json(self, url_fragment, params=None, json=None, headers=None):
        if not headers:
            headers = {"Accept": "application/json"}
            
        #params["analysis_server"] = params.get("analysis_server", self.analysis_server)
        
        response = requests.post(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers, timeout=self.timeout)
        #response.raise_for_status()
        return parse_response(response)
    
    def put2code(self, url_fragment, params=None, json=None, headers=None):
        #response = requests.post(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers)
        #params["analysis_server"] = params.get("analysis_server", self.analysis_server)
        
        response = requests.put(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers, timeout=self.timeout)
        #response.raise_for_status()
        return http_success(response)
    
    def put2json(self, url_fragment, params=None, json=None, headers=None):
        if not headers:
            headers = {"Accept": "application/json"}
        #params["analysis_server"] = params.get("analysis_server", self.analysis_server)
        
        response = requests.put(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers, timeout=self.timeout)
        #response.raise_for_status()
        return parse_response(response)
    
    def delete2code(self, url_fragment, params=None, json=None, headers=None):
        #params["analysis_server"] = params.get("analysis_server", self.analysis_server)
        
        response = requests.delete(self.build_url(url_fragment), auth=(self.user, self.password), params=params, json=json, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        #return self.parse_response(response)
        return http_success(response)
        
    """
    def api_get(self, url, no_accept_json=False, **kwargs):
        #this will set the default if the KEY maxResult does not exist
        #if it's been specifically set to None, this won't overwrite that
        kwargs["maxResults"] = kwargs.get("maxResults", 1000)
        
        headers = kwargs.get("headers", {'Accept':'application/json'})
        if "headers" in kwargs.keys():    
            del kwargs["headers"]
        
        kwargs = camelify_kwargs(kwargs)
        
        result = requests.get('http://{}:{}{}'.format(self.host, self.port, url), auth=(self.user, self.password), params=kwargs, headers=headers)
        #print result.url
        return result
        
    def wrapped_api_get(self, url_end, **kwargs):
        
        if self.version:
            url = "/api/%s/%s" % (self.version, url_end, )
        else:
            url = "/api/%s" % (url_end, )
        
        #we have to do this to promote anything passed in as "params" into the upper level
        #this might bite me later but the API calls will get ugly if you have to splat the dict inline
        kwargs = promote_params(kwargs)
        
        response = self.api_get(url, **kwargs)
        
        return parse_response(response)
    
    
    def api_post(self, url, **kwargs):
        
        headers = kwargs.get("headers", {'Accept':'application/json'})
        json = kwargs.get("json", None)
        if json:
            del kwargs['json']
        
        kwargs = camelify_kwargs(kwargs)
        #kwargs = self.fix_true_false(kwargs)
        
        return requests.post('http://{}:{}{}'.format(self.host, self.port, url), auth=(self.user, self.password), params=kwargs, json=json, headers=headers)
        #return requests.post('http://{}:{}{}'.format(self.host, self.port, url), auth=(self.user, self.password), params=kwargs, json=json)
    
    
    def wrapped_api_post(self, url_fragment, **kwargs):
        if self.version:
            url = "/api/%s/%s" % (self.version, url_fragment, )
        else:
            url = "/api/%s" % (url_fragment, )
        
        kwargs = promote_params(kwargs)
        
        response = self.api_post(url, **kwargs)
        
        return parse_response(response)
    
    def api_put(self, url, **kwargs):
            
        headers = kwargs.get("headers", {'Accept':'application/json'})
        json = kwargs.get("json", None)
        if json:
            del kwargs['json']
        
        kwargs = camelify_kwargs(kwargs)
        #kwargs = self.fix_true_false(kwargs)
        
        return requests.put('http://{}:{}{}'.format(self.host, self.port, url), auth=(self.user, self.password), params=kwargs, headers=headers)
    
    def wrapped_api_put(self, url_end, **kwargs):
        if self.version:
            url = "/api/%s/%s" % (self.version, url_end, )
        else:
            url = "/api/%s" % (url_end, )
        
        kwargs = promote_params(kwargs)
        
        response = self.api_put(url, **kwargs)
        
        return parse_response(response)
    
    def api_delete(self, url, **kwargs):
        
        headers = kwargs.get("headers", {'Accept':'application/json'})
        
        kwargs = camelify_kwargs(kwargs)
        #kwargs = self.fix_true_false(kwargs)
        
        return requests.delete('http://{}:{}{}'.format(self.host, self.port, url), auth=(self.user, self.password), headers=headers)
    
    def wrapped_api_delete(self, url_end, **kwargs):
        if self.version:
            url = "/api/%s/%s" % (self.version, url_end, )
        else:
            url = "/api/%s" % (url_end, )
        
        #I don't think we need to hoist out the json, like for the POST/PUT
        
        #I didn't think we needed to promote kwargs, but the multi-sensor delete uses query params not just a URL
        kwargs = promote_params(kwargs)
        
        response = self.api_delete(url, **kwargs)
        
        print_debug(response)
        
        response.raise_for_status()
        
        #return self.parse_response(response)
        return http_success(response)
    """
    
    """
    SECURITY ROLES!
    """
    def get_security_roles(self, **kwargs):
            return self.get2json("security-roles", params=kwargs)
        
    def get_security_role_details(self, role_id):
        return self.get2json("security-roles/%s" % (str(role_id), ))
    
    def create_security_role(self, name, description, permission_list, user_list):
        data_dict = {
            "name": name,
            "description": description,
            "permissions": {
                "permission": dictize_list("id", permission_list),
            },
            "users":{
                "user": dictize_list("id", user_list),
            },
        }
        
        return self.post2json("security-roles", json=data_dict)
    
    def update_security_role(self, role_id, name, description, permission_list, user_list):
        data_dict = {
            "id": role_id,
            "name": name,
            "description": description,
            "permissions": {
                "permission": dictize_list("id", permission_list),
            },
            "users":{
                "user": dictize_list("id", user_list),
            },
        }
        
        return self.put2json("security-roles/%s" % (role_id, ), json=data_dict)
    
    def remove_security_role(self, role_id):
        return self.delete2code("security-roles/%s" % (role_id, ))
    
    def add_users_to_role(self, role_id, user_id_list):
        return self.post2code("security-roles/%s/add-users" % (role_id, ), params={"userID": user_id_list})
        
    def remove_users_from_role(self, role_id, user_id_list):
        return self.post2code("security-roles/%s/remove-users" % (role_id, ), params={"userID": user_id_list})
    
    def set_users_for_role(self, role_id, user_id_list):
        return self.post2code("security-roles/%s/set-users" % (role_id, ), params={"userID": user_id_list})
    
    """
    PERMISSIONS!
    """
    
    def get_permissions(self, **kwargs):
        return self.get2json("permissions", params=kwargs)
    
    """
    USERS!
    """
    def get_users(self, **kwargs):
        return self.get2json("users", params=kwargs)
    
    def get_user_details(self, user_id):
        return self.get2json("users/%s" % (str(user_id), ))
    
    def get_user_groups(self, user_id):
        return self.get2json("users/%s/user-groups" % (str(user_id), ))
    
    def get_current_user(self):
        return self.get2json("users/current")
    
    def get_user_roles(self, user_id):
        return self.get2json("users/%s/security-roles" % (str(user_id), ))
    
    def get_user_permissions(self, user_id):
        return self.get2json("users/%s/permissions" % (str(user_id), ))
    
    def get_user_authorized_sensors(self, user_id):
        return self.get2json("users/%s/authorized-sensors" % (str(user_id), ))
    
    def create_user(self, username, password, first_name, last_name, email, phone_number, mobile_number, fax_number, \
        prefers_html_email, prefers_attached_video, locale, group_id_list, authorized_sensor_id_list, security_role_id_list):
        
        data_dict = {
            "username": username,
            "password": password,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phoneNumber": phone_number,
            "mobileNumber": mobile_number,
            "faxNumber": fax_number,
            "prefersHtmlEmail": prefers_html_email,
            "prefersAttachedVideoClips": prefers_attached_video,
            "locale": locale,
            "userGroup": dictize_list("id", group_id_list),
            "authorizedSensors": dictize_list("id", authorized_sensor_id_list),
            "securityRoles": dictize_list("id", security_role_id_list),
        }
    
        return self.post2json("users", json=data_dict)
    
    def update_user(self, user_id, username, password, first_name, last_name, email, phone_number, mobile_number, fax_number, \
        prefers_html_email, prefers_attached_video, locale, group_id_list, authorized_sensor_id_list, security_role_id_list):
        
        data_dict = {
            "id": user_id,
            "username": username,
            "password": password,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phoneNumber": phone_number,
            "mobileNumber": mobile_number,
            "faxNumber": fax_number,
            "prefersHtmlEmail": prefers_html_email,
            "prefersAttachedVideoClips": prefers_attached_video,
            "locale": locale,
            "userGroup": dictize_list("id", group_id_list),
            "authorizedSensors": dictize_list("id", authorized_sensor_id_list),
            "securityRoles": dictize_list("id", security_role_id_list),
        }
    
        return self.put2json("users/%s" % (user_id, ), json=data_dict)
    
    def set_user_groups(self, user_id, group_id_list):
        return self.post2code("users/%s/set-user-gropus" % (user_id, ), params={"userGroupID": group_id_list})
    
    def set_user_security_roles(self, user_id, security_role_id_list):
        return self.post2code("users/%s/set-security-roles" % (user_id, ), params={"securityRoleID": security_role_id_list})
    
    def set_user_authorized_sensors(self, user_id, sensor_id_list):
        return self.post2code("users/%s/set-authorized-sensors" % (user_id, ), params={"userID": user_id, "sensorID": sensor_id_list})
    
    def remove_user(self, user_id):
        return self.delete2code("users/%s" % (user_id, ))
    
    """
    GROUPS!
    """
    def get_groups(self, **kwargs):
        return self.get2json("groups", params=kwargs)
    
    def get_group_details(self, group_id):
        return self.get2json("user-groups/%s" % (str(group_id), ))
    
    def get_group_authorized_sensors(self, group_id):
        return self.get2json("user-groups/%s/authorized-sensors" % (str(group_id), ))
    
    def create_group(self, name, user_id_list):
        data_dict = {
            "name": name,
            "users":{
                "user": dictize_list("id", user_id_list)
            }
        }
        
        return self.post2json("user-groups", json=data_dict)
    
    def update_group(self, user_group_id, name, user_id_list):
        data_dict = {
            "groupID": user_group_id,
            "name": name,
            "users":{
                "user": dictize_list("id", user_id_list)
            }
        }
        
        return self.put2json("user-groups/%s" % (str(user_group_id), ), json=data_dict)
    
    def add_users_to_group(self, user_group_id, user_id_list):
        return self.post2code("user-groups/%s/add-users" % (str(user_group_id), ), params={"userID": user_id_list})
    
    def remove_users_from_group(self, user_group_id, user_id_list):
        return self.post2code("user-groups/%s/remove-users" % (str(user_group_id), ), params={"userID": user_id_list})
    
    def set_group_users(self, user_group_id, user_id_list):
        return self.post2code("user-groups/%s/set-users" % (str(user_group_id), ), params={"userID": user_id_list})
    
    def set_group_sensors(self, user_group_id, sensor_id_list):
        return self.post2code("user-groups/%s/set-authorized-sensors" % (str(user_group_id), ), params={"sensorID": sensor_id_list})
    
    def remove_group(self, group_id):
        return self.delete2code("user-groups/%s" % (str(group_id), ))
    
    
    """
    SERVERS!
    """
    def get_servers(self, **kwargs):
        return self.get2json("aisight-servers", params=kwargs)
    
    def get_server_details(self, server_id):
        return self.get2json("aisight-servers/%s" % (str(server_id), ))
    
    def create_server(self, name, description, ipOrDns):
        data_dict = {
            "name": name,
            "description": description,
            "ipOrDns": ipOrDns,
        }
        
        return self.post2json("aisight-servers", json=data_dict)
    
    def update_server(self, server_id, name, description, ipOrDns):
        data_dict = {
            "id": server_id,
            "name": name,
            "description": description,
            "ipOrDns": ipOrDns,
        }
        
        return self.put2json("aisight-servers/%s" % (server_id, ), json=data_dict)
    
    def remove_server(self, server_id):
        return self.delete2code("aisight-servers/%s" % (server_id, ))
    
    """
    SENSORS TYPES!
    """
    def get_sensor_type_categories(self, **kwargs):
        return self.get2json("sensor-type-categories", params=kwargs)
    
    def get_sensor_types(self, **kwargs):
        return self.get2json("sensor-types", params=kwargs)
    
    def get_sensor_type_details(self, sensor_type_id):
        return self.get2json("sensor-types/%s" % (str(sensor_type_id), ))
    
    def create_sensor_type(self, name, description, manufacturer, model, sensor_category_id):
        data_dict = {
            "name": name,
            "description": description,
            "manufacturer": manufacturer,
            "model": model,
            "sensorTypeCategory": {
                "id": sensor_category_id,
            },
        }
        
        return self.post2json("sensor-types", json=data_dict)
    
    def update_sensor_type(self, sensor_type_id, name, description, manufacturer, model, sensor_category_id):
        data_dict = {
            "id": sensor_type_id, 
            "name": name,
            "description": description,
            "manufacturer": manufacturer,
            "model": model,
            "sensorTypeCategory": {
                "id": sensor_category_id,
            },
        }
        
        return self.put2json("sensor-types", json=data_dict)
    
    def delete_sensor_type(self, sensor_type_id):
        return self.delete2code("sensor-types/%s" % (sensor_type_id, ))
    
    
    """
    SENSORS!
    """    
    def get_sensors(self, **kwargs):
        return self.get2json("sensors", params=kwargs)
        #return self.wrapped_api_get("sensors", **kwargs)
    
    def get_sensor_details(self, sensor_id):
        return self.get2json("sensors/%s" % (str(sensor_id), ))
    
    def get_sensors_state(self):
        return self.get2json("sensors/state")
        
    def get_sensor_state(self, sensor_id):
        return self.get2json("sensors/%s/state" % (str(sensor_id), ))
    
    def create_sensor(self, **kwargs):
        return self.post2json("sensors", params=kwargs)
    
    def update_sensor(self, sensor_id, **kwargs):
        return self.put2json("sensors/%s" % (str(sensor_id), ), params=kwargs)
    
    #some of these are required, others are not
    #what's the best ordering?  seems lik required first, optional as kwargs
    #but is that the best?
    def create_scada_sensor(self, name,  \
                            #SCADA specific stuff
                            engineering_low, engineering_high, engineering_units, update_interval, 
                            #universal bookkeeping
                            alerting_odds, alert_suppression_period, aisight_server_id, \
                            #now we start to get into the defaulted values, so they're named
                            comments_required=False, globally_visible=False, 
                            #these are optional and so if you don't have to send them, they have to be named
                            user_id_list=None, user_groups_id_list=None, sensor_groups_id_list=None, \
                            #these are optional, and thus also named
                            description=None, serial_number=None, part_number=None, latitude=None, longitude=None):
        
        data_dict = {
            "sensorType": {"id": 8},
            "name": name,
            "engineeringLow": engineering_low,
            "engineeringHigh": engineering_high,
            "engineeringUnits": engineering_units,
            "updateInterval": update_interval,
            "alertingOdds": alerting_odds,
            "alertSuppressionPeriod": alert_suppression_period,
            "analysisServer": {"id": aisight_server_id},
            "commentsRequired": comments_required,
            "globallyVisible": globally_visible,
        }
        
        if not engineering_units:
            del data_dict["engineeringUnits"]
        
        if user_id_list:
            data_dict["users"] = {"user": self.dictize_list("id", user_id_list)}
            
        if user_groups_id_list:
            data_dict["userGroups"] = {"userGroup": self.dictize_list("id", user_groups_id_list)}
            
        if sensor_groups_id_list:
            data_dict["sensorGroups"] = {"sensorGroup": self.dictize_list("id", sensor_groups_id_list)}
            
        if description:
            data_dict["description"] = description
            
        if serial_number:
            data_dict["serialNumber"] = serial_number
            
        if part_number:
            data_dict["partNumber"] = part_number
            
        if latitude:
            data_dict["latitude"] = latitude
            
        if longitude:
            data_dict["longitude"] = longitude
            
        #return self.wrapped_api_post("sensors", json=data_dict)
        return self.post2json("sensors", params=None, json=data_dict)
    
    def update_scada_sensor(self):
        raise NotImplemented()
    
    def create_composite_sensor(self, name,  \
                            #specific to composites
                            sensor_id_list, 
                            #universal bookkeeping
                            alerting_odds, alert_suppression_period, aisight_server_id, \
                            #now we start to get into the defaulted values, so they're named
                            comments_required=False, globally_visible=False, 
                            #these are optional and so if you don't have to send them, they have to be named
                            user_id_list=None, user_groups_id_list=None, sensor_groups_id_list=None, \
                            #these are optional, and thus also named
                            description=None, serial_number=None, part_number=None, latitude=None, longitude=None):
        
        data_dict = {
            "sensorType": {"id": 7},
            "name": name,
            "alertingOdds": alerting_odds,
            "alertSuppressionPeriod": alert_suppression_period,
            "analysisServer": {"id": aisight_server_id},
            "commentsRequired": comments_required,
            "globallyVisible": globally_visible,
            "sensors": {
                "sensor": dictize_list("id", sensor_id_list), 
            }
        }
        
        if user_id_list:
            data_dict["users"] = {"user": self.dictize_list("id", user_id_list)}
            
        if user_groups_id_list:
            data_dict["userGroups"] = {"userGroup": self.dictize_list("id", user_groups_id_list)}
            
        if sensor_groups_id_list:
            data_dict["sensorGroups"] = {"sensorGroup": self.dictize_list("id", sensor_groups_id_list)}
            
        if description:
            data_dict["description"] = description
            
        if serial_number:
            data_dict["serialNumber"] = serial_number
            
        if part_number:
            data_dict["partNumber"] = description
            
        if latitude:
            data_dict["latitude"] = latitude
            
        if longitude:
            data_dict["longitude"] = longitude
            
        #return self.wrapped_api_post("sensors", json=data_dict)
        return self.post2json("sensors", params=None, json=data_dict)
        
    def update_composite_sensor(self):
        raise NotImplemented()
    
    def create_video_sensor(self, name, url, \
                            #universal bookkeeping
                            alerting_odds, alert_suppression_period, aisight_server_id, \
                            #these are video only, but not required
                            target_fps=None, target_width=None, target_height=None, \
                            alert_clip_length=None, post_alert_clip_length=None, alert_clip_text_color=None, \
                            full_trajectory_clip=None, thermal_camera=None, \
                            #now we start to get into the defaulted values, so they're named
                            comments_required=False, globally_visible=False, \
                            #these are optional and so if you don't have to send them, they have to be named
                            user_id_list=None, user_groups_id_list=None, sensor_groups_id_list=None, \
                            #these are optional, and thus also named
                            description=None, serial_number=None, part_number=None, latitude=None, longitude=None):
        
        data_dict = {
            "sensorType": {"id": 1},
            "name": name,
            "url": url,
            "alertingOdds": alerting_odds,
            "alertSuppressionPeriod": alert_suppression_period,
            "analysisServer": {"id": aisight_server_id},
            "commentsRequired": comments_required,
            "globallyVisible": globally_visible,
        }
        
        if target_fps:
            data_dict['targetFPS'] = target_fps
        
        if target_width:
            data_dict['targetWidth'] = target_width
            
        if target_height:
            data_dict['targetHeight'] = target_height
            
        if alert_clip_length:
            data_dict['alertClipLength'] = alert_clip_length
            
        if post_alert_clip_length:
            data_dict['postAlertClipLength'] = post_alert_clip_length
            
        if alert_clip_text_color:
            data_dict['alertClipTextColor'] = alert_clip_text_color
            
        if full_trajectory_clip:
            data_dict['fullTrajectoryClip'] = full_trajectory_clip
            
        if thermal_camera:
            data_dict['thermalCamera'] = thermal_camera
            
        
        if user_id_list:
            data_dict["users"] = {"user": self.dictize_list("id", user_id_list)}
            
        if user_groups_id_list:
            data_dict["userGroups"] = {"userGroup": self.dictize_list("id", user_groups_id_list)}
            
        if sensor_groups_id_list:
            data_dict["sensorGroups"] = {"sensorGroup": self.dictize_list("id", sensor_groups_id_list)}
            
        if description:
            data_dict["description"] = description
            
        if serial_number:
            data_dict["serialNumber"] = serial_number
            
        if part_number:
            data_dict["partNumber"] = part_number
            
        if latitude:
            data_dict["latitude"] = latitude
            
        if longitude:
            data_dict["longitude"] = longitude
            
        #return self.wrapped_api_post("sensors", json=data_dict)
        return self.post2json("sensors", params=None, json=data_dict)
    
    def update_video_sensor(self):
        raise NotImplemented()
    
    def create_image_sensor(self):
        raise NotImplemented()
    
    def update_image_sensor(self):
        raise NotImplemented()
    
    def create_audio_sensor(self):
        raise NotImplemented()
    
    def update_audio_sensor(self):
        raise NotImplemented()
    
    """
    def create_sensor(self, name, description, serial_number, part_number, url, latitude, longitude, \
                      engineering_low, engineering_high, engineering_units, update_interval, \
                      target_fps, target_width, target_height, alert_clip_length, post_alert_clip_length, alert_clip_text_color, \
                      full_trajectory_clip, thermal_camera, alerting_odds, alert_suppression_period, \
                      sensor_type_id, aisight_server_id, sensors, comments_required, globally_visible, user_ids, user_group_ids, sensor_group_ids):
        data_dict = {
            "name": name,
            "description": description,
            "serialNumber": serial_number,
            "partNumber": part_number,
            "url": url,
            "latitude": latitude,
            "longitude": longitude,
            "sensorTypeCategory": {
                "id": sensor_category_id,
            },
        }
        
        return self.wrapped_api_post("sensor-types", data_dict)
    
    def update_sensor(self, sensor_type_id, name, description, manufacturer, model, sensor_category_id):
        data_dict = {
            "id": sensor_type_id, 
            "name": name,
            "description": description,
            "manufacturer": manufacturer,
            "model": model,
            "sensorTypeCategory": {
                "id": sensor_category_id,
            },
        }
        
        return self.wrapped_api_post("sensor-types", data_dict)
    """
    
    def start_all_sensors(self):
        params = {"mode": "all"}
        return self.post2code("sensors/start", params=params)
    
    def start_sensors(self, sensor_id_list):
        params = {"mode": "sensor", "sensorId": sensor_id_list}
        #return self.wrapped_api_post("sensors/start", params=params)
        return self.post2code("sensors/start", params=params)
    
    def start_sensor_groups(self, sensor_group_id_list):
        params = {"mode": "group", "sensorGroupId": sensor_group_id_list}
        return self.post2code("sensors/start", params=params)
    
    def start_sensor(self, sensor_id):
        #return self.wrapped_api_post("sensors/%s/start" % (str(sensor_id), ) )
        return self.post2code("sensors/%s/start" % (sensor_id, ))
    
    def stop_all_sensors(self):
        params = {"mode": "all"}
        return self.post2code("sensors/stop", params=params)
    
    def stop_sensors(self, sensor_id_list):
        params = {"mode": "sensor", "sensorId": sensor_id_list}
        #return self.wrapped_api_post("sensors/stop", params=params)
        return self.post2code("sensors/start", params)
    
    def stop_sensor_groups(self, sensor_group_id_list):
        params = {"mode": "group", "sensorGroupId": sensor_group_id_list}
        return self.post2code("sensors/stop", params=params)
    
    def stop_sensor(self, sensor_id):
        #return self.wrapped_api_post("sensors/%s/stop" % (str(sensor_id), ) )
        return self.post2code("sensors/%s/stop" % (sensor_id, ))
    
    def reset_sensors(self, sensor_id_list=None, sensor_group_id_list=None):
        params = {"sensorId": sensor_id_list, "sensorGroupId": sensor_group_id_list}
        return self.post2code("sensors/reset", params=params)
    
    def reset_sensor(self, sensor_id):
        return self.post2code("sensors/%s/reset" % (str(sensor_id), ) )
    
    def delete_sensors(self, sensor_id_list, delete_alerts=True):
        params = {"sensorId": sensor_id_list, "deleteAlerts": delete_alerts}
        return self.delete2json("sensors", params=params)
    
    def delete_sensor(self, sensor_id):
        #return self.wrapped_api_delete("sensors/%s" % (str(sensor_id), ) )
        return self.delete2code("sensors/%s" % (str(sensor_id), ))
    
    """
    SENSOR GROUPS!
    """
    def get_sensor_groups(self, **kwargs):
        return self.get2json("sensor-groups", params=kwargs)
    
    def get_sensor_group_details(self, sensor_group_id, **kwargs):
        #params = {"unreviewedCounts": unreviewed_counts}
        return self.get2json("sensor-groups/%s" % (str(sensor_group_id), ), params=kwargs)

    def set_sensor_parent_group(self, sensor_group_id, parent_sensor_group_id):
        params = {"parentGroupId": parent_sensor_group_id, }
        return self.post2code("sensor-groups/%s/set-parent-group" % (str(sensor_group_id), ), params=params)
    
    def create_sensor_group(self):
        raise NotImplemented()
    
    def update_sensor_group(self):
        raise NotImplemented()
    
    def delete_sensor_group(self, sensor_group_id):
        return self.delete2code("sensor-groups/%s" % (str(sensor_group_id), ) )
    
    def create_child_sensor_group(self):
        raise NotImplemented()
    
    def add_sensor_to_group(self, sensor_group_id, sensor_id):
        return self.post2code("sensor-groups/%s/add-child-sensor" % (str(sensor_group_id), ), params={"sensorID": sensor_id})
    
    def remove_sensor_from_group(self, sensor_group_id, sensor_id):
        return self.post2code("sensor-groups/%s/remove-child-sensor" % (str(sensor_group_id), ), params={"sensorID": sensor_id})
    
    def set_sensors_for_group(self, sensor_group_id, sensor_id_list):
        return self.post2code("sensor-groups/%s/set-child-sensors" % (str(sensor_group_id), ), params={"sensorID": sensor_id_list})
    
    
    """
    ALERTS!
    """
    def get_alerts(self, **kwargs):
        return self.get2json("alerts", params=kwargs)
    
    def get_alert_count(self, **kwargs):
        return self.get2text("alerts/count", params=kwargs)
    
    def get_alerts_incoming(self, last_alert_id=None, sensor_id_list=None, timeout=None):
        data_dict = {}
        if last_alert_id:
            data_dict["lastAlertId"] = last_alert_id
        if sensor_id_list:
            data_dict["sensorId"] = sensor_id_list
        if timeout:
            data_dict["timeout"] = timeout
        return self.get2json("alerts/incoming", params=data_dict)
    
    def get_alert_details(self, alert_id):
        return self.get2json("alerts/%s" % (str(alert_id), ))
    
    def get_alert_image(self, alert_id):
        return self.get2json("alerts/%s/image" % (str(alert_id), ))
    
    #GET /api/v1.1/alerts/{alertID}/videoclip (mov/mp4/webm)
    def get_alert_video(self, alert_id, video_type=None):
        if not video_type:
            video_type=""
        else:
            video_type = "/" + video_type
        
        return self.get2json("alerts/%s/video%s" % (str(alert_id), video_type))
    
    def set_all_alerts_status(self, reviewed=True):
        if reviewed:
            status=3
        else:
            status=1
        params = {"allAlerts": True, "reviewedStatus": status}
        return self.post2code("alerts/set-reviewed-status", params=params)
    
    def set_alert_status(self, alert_id, reviewed=True):
        if reviewed:
            status=3
        else:
            status=1
        params = {"allAlerts": False, "alertId": alert_id, "reviewedStatus": status}
        return self.post2code("alerts/set-reviewed-status", params=params)
    
    def set_alerts_status(self, alert_id_list, reviewed=True):
        if reviewed:
            status=3
        else:
            status=1
        params = {"allAlerts": False, "alertId": alert_id_list, "reviewedStatus": status}
        return self.post2code("alerts/set-reviewed-status", params=params)
    
    def set_alert_important(self, alert_id, important=True):
        params = {"alertId": alert_id, "important": important}
        return self.post2code("alerts/set-important-flag", params=params)
    
    def set_alerts_important(self, alert_id_list, important=True):
        params = {"alertId": alert_id_list, "important": important}
        return self.post2code("alerts/set-important-flag", params=params)
    
    def get_alert_comments(self, alert_id):
        return self.get2json("alerts/%s/comments" % (str(alert_id),))
    
    def add_alert_comment(self, alert_id, comment):
        return self.wrapped_api_post("alerts/%s/comments" % (str(alert_id),), {"commentText": comment})
    
    def update_alert_comment(self, alert_id, comment_id, comment):
        return self.wrapped_api_post("alerts/%s/comments/%s" % (str(alert_id), str(comment_id), ), {"commentText": comment})
    
    def delete_alert_comment(self, alert_id, comment_id):
        return self.delete2code("alerts/%s/comments/%s" % (str(alert_id), str(comment_id), ))
    
    def send_alert_email(self, alert_id, user_id_list, group_id_list, email_subject, email_from_name, email_from_address):
        data_dict = {
            "userId": user_id_list,
            "userGroupId": group_id_list,
            "emailSubject": email_subject,
            "emailFromName": email_from_name,
            "emailFromAddress": email_from_address,
        }
        
        return self.wrapped_api_post("alerts/%s/email-alert" % (str(alert_id), ), params=data_dict)
    
    def delete_alert(self, alert_id):
        raise NotImplemented()
    
    def delete_alerts(self, alert_id_list):
        params = {'alertId': alert_id_list}
        return self.delete2code("alerts", params=params)
    
    def delete_alerts_by_filter(self):
        #this seems to be all the same as the GET method filter
        raise NotImplemented()
    
    """
    SYSTEM EVENTS!
    """
    def get_system_events(self, **kwargs):
        return self.get2json("system-events", params=kwargs)
    
    def get_system_events_count(self, **kwargs):
        return self.get2json("system-events/count", params=kwargs)
    
    def get_system_events_incoming(self, last_system_event_id=None, sensor_id_list=None, timeout=None):
        data_dict = {}
        if last_system_event_id:
            data_dict["lastSystemEventId"] = last_system_event_id
        if sensor_id_list:
            data_dict["sensorId"] = sensor_id_list
        if timeout:
            data_dict["timeout"] = timeout
        return self.get2json("system-events/incoming", params=data_dict)
    
    def get_system_event_details(self, system_event_id):
        return self.get2json("system-events/%s" % (str(system_event_id), ))
    
    def get_system_event_image(self, system_event_id):
        return self.get2json("system-events/%s/image" % (str(system_event_id), ))
    
    def set_system_events_status(self, system_events_list):
        raise NotImplemented()
    
    def delete_system_event(self, system_event_id):
        return self.delete2code("system-events/%s" % (str(system_event_id), ))
    
    def delete_system_events(self, system_event_id_list):
        params = {'systemEventId': system_event_id_list}
        return self.delete2code("system-events", params=params)
    
    def delete_system_events_by_filter(self):
        raise NotImplemented()
    
    """
    NOTIFICATIONS!
    """
    def get_notifications(self, **kwargs):
        return self.get2json("notifications", params=kwargs)
    
    def get_notification_details(self, notification_id):
        return self.get2json("notifications/%s" % (str(notification_id), ))
    
    def create_notification(self):
        raise NotImplemented()
    
    def update_notification(self):
        raise NotImplemented()
    
    def delete_notification(self, notification_id):
        return self.delete2code("notifications/%s" % (str(notification_id), ))
    
    """
    AUDIT LOG!
    GET /api/auditlog
    GET /api/auditlog/{auditLogId}
    GET /api/auditlog-settings
    """
    def get_auditlog(self, **kwargs):
        return self.get2json("auditlog", params=kwargs)
    
    def get_auditlog_details(self, auditlog_id):
        return self.get2json("auditlog/%s" % (str(auditlog_id), ))
    
    def get_auditlog_settings(self):
        return self.get2json("auditlog-settings")
    
    def update_auditlog_settings(self):
        raise NotImplemented()
    
    """
    VERSIONS!
    """
    
    def get_version(self):
        #response = self.api_get("/api/utils/version", maxResults=None, headers=None)
        #return response.text
        return self.get2text("utils/version")
    
    def get_api_version(self):
        #response = self.api_get("/api/utils/api-version", maxResults=None, headers=None)
        #return response.text
        return self.get2text("utils/api-version")
    
    
    """
    DASHBOARD!
    """
    def get_dashboard(self):
        return self.get2json("dashboard")
                
if __name__ == "__main__":
    
    #data_file = open("em_api_data.txt", "w")
    #em = EMConnector(version="v1.1")
    em = EMConnector()
    
    print em.get_version()
    print em.get_api_version()

    """
    methods = dir(em)
    
    total = 0
    success = 0
    fail = 0
    
    for method in methods:
        if "get_" in method:
            total += 1
            try:
                func = getattr(em, method)
                argspec = inspect.getargspec(func)
                
                if len(argspec.args) == 2:
                    print "passing a value..."
                    pprint.pprint( func(1), data_file)
                else:
                    pprint.pprint( func(), data_file)
                    
                print "Success executing %s" % method
                success += 1
            except:
                print "Problem executing %s" % method
                fail += 1
                
                
    print "Tried executing %d methods with %d succeeding and %d failing" % (total, success, fail)
    """