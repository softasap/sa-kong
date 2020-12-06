import os
import json
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_postgres_running_and_enabled(host):
    if host.system_info.distribution == 'centos':
        assert not host.ansible(
            "service",
            "name=postgresql-9.6 enabled=true state=started")['changed']
    if host.system_info.distribution == 'debian':
        assert not host.ansible(
            "service",
            "name=postgres enabled=true state=started")['changed']


def test_kong_running_and_enabled(host):
    assert not host.ansible(
        "service",
        "name=kong enabled=true state=started")['changed']


def test_kong_listens_on_ports(host):
    # 8000 on which Kong listens for incoming HTTP traffic
    #  from your clients, and forwards it to your upstream services.
    assert host.socket("tcp://0.0.0.0:8000").is_listening
    # 8001 on which the Admin API used to configure Kong listens.
    assert host.socket("tcp://0.0.0.0:8001").is_listening
    # 8443 on which Kong listens for incoming HTTPS traffic.
    # This port has a similar behavior as the :8000 port,
    # except that it expects HTTPS traffic only. This port can be
    # disabled via the configuration file.

    # 8444 on which the Admin API listens for HTTPS traffic.


def test_kong_service_can_be_created(host):
    service_create_cmd = """
        curl -i -X POST \
        --url http://localhost:8001/services/ \
        --data 'name=example-service' \
        --data 'url=http://mockbin.org'
    """
    service_result = host.run(service_create_cmd)
    print(service_result)
    assert service_result.rc == 0
    assert "HTTP/1.1 201 Created" in service_result.stdout


def test_kong_service_route_can_be_created(host):
    kong_cmd = """
        curl -i -X POST \
        --url http://localhost:8001/services/example-service/routes \
        --data 'hosts[]=example.com'
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 201 Created" in kong_result.stdout


def test_kong_request_is_served(host):
    kong_cmd = """
        curl -i -X GET \
        --url http://localhost:8000/ \
        --header 'Host: example.com'
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 200 OK" in kong_result.stdout


def test_kong_keyauth_plugin_can_be_associated(host):
    kong_cmd = """
        curl -i -X POST \
        --url http://localhost:8001/services/example-service/plugins/ \
        --data 'name=key-auth'
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 201 Created" in kong_result.stdout


def test_kong_keyauth_plugin_properly_configured(host):
    kong_cmd = """
        curl -i -X GET \
        --url http://localhost:8000/ \
        --header 'Host: example.com'
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 401 Unauthorized" in kong_result.stdout
    assert "No API key found in request" in kong_result.stdout


def test_kong_consumer_can_be_created(host):
    kong_cmd = """
        curl -i -X POST \
        --url http://localhost:8001/consumers/ \
        --data "username=Jason"
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 201 Created" in kong_result.stdout


def test_kong_consumer_key_credentials_can_be_provisioned(host):
    kong_cmd = """
        curl -i -X POST \
        --url http://localhost:8001/consumers/Jason/key-auth/ \
        --data 'key=ENTER_KEY_HERE'
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 201 Created" in kong_result.stdout


def test_kong_consumer_key_credentials_can_be_used(host):
    kong_cmd = """
        curl -i -X GET \
        --url http://localhost:8000 \
        --header "Host: example.com" \
        --header "apikey: ENTER_KEY_HERE"
    """
    kong_result = host.run(kong_cmd)
    print(kong_result)
    assert kong_result.rc == 0
    assert "HTTP/1.1 200 OK" in kong_result.stdout


def test_kong_route_can_be_deleted(host):
    service_cmd = """
        curl http://localhost:8001/services/example-service/routes/
    """
    kong_result = host.run(service_cmd)
    routes = json.loads(kong_result.stdout)
    print(kong_result)
    assert kong_result.rc == 0
    route_id = routes['data'][0]['id']
    delete_service_cmd = """
    curl -X DELETE \
    http://localhost:8001/services/example-service/routes/""" + route_id
    route_delete_result = host.run(delete_service_cmd)
    assert "Not found" not in route_delete_result.stdout


def test_kong_consumer_can_be_deleted(host):
    service_cmd = """
        curl -X DELETE http://localhost:8001/consumers/Jason
    """
    service_result = host.run(service_cmd)
    print(service_result)
    assert service_result.rc == 0


def test_kong_service_can_be_deleted(host):
    service_cmd = """
        curl -X DELETE http://localhost:8001/services/example-service
    """
    service_result = host.run(service_cmd)
    print(service_result)
    assert service_result.rc == 0


def test_kong_plugin_upstream_auth_basic_installed(host):
    check_plugin_present_cmd = """
        luarocks list | grep kong-plugin-upstream-auth-basic
    """
    cmd_result = host.run(check_plugin_present_cmd)
    print(cmd_result)
    assert cmd_result.rc == 0
    assert "kong-plugin-upstream-auth-basic" in cmd_result.stdout


def test_kong_plugin_sa_jwt_claims_validate_installed(host):
    check_plugin_present_cmd = """
        luarocks list | grep kong-plugin-sa-jwt-claims-validate
    """
    cmd_result = host.run(check_plugin_present_cmd)
    print(cmd_result)
    assert cmd_result.rc == 0
    assert "kong-plugin-sa-jwt-claims-validate" in cmd_result.stdout
