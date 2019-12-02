sa-kong
=======

[![Build Status](https://travis-ci.org/softasap/sa-kong.svg?branch=master)](https://travis-ci.org/softasap/sa-kong)


Kong is a scalable, open source API Layer (also known as an API Gateway, or API Middleware). Kong runs in front of any RESTful API and is extended through Plugins, which provide extra functionality and services beyond the core platform.

Kong was originally built at Mashape to secure, manage and extend over 15,000 APIs & Microservices for its API Marketplace, which generates billions of requests per month for over 200,000 developers. Today Kong is used in mission critical deployments at small and large organizations.

Scalable: Kong easily scales horizontally by simply adding more machines, meaning your platform can handle virtually any load while keeping latency low.

Modular: Kong can be extended by adding new plugins, which are easily configured through a RESTful Admin API.

Runs on any infrastructure: Kong runs anywhere. You can deploy Kong in the cloud or on-premise environments, including single or multi-datacenter setups and for public, private or invite-only APIs.


You’ve probably heard that Kong is built on Nginx, leveraging its stability and efficiency. But how is this possible exactly?

To be more precise, Kong is a Lua application running in Nginx and made possible by the lua-nginx-module. Instead of compiling Nginx with this module, Kong is distributed along with OpenResty, which already includes lua-nginx-module. OpenResty is not a fork of Nginx, but a bundle of modules extending its capabilities.

This sets the foundations for a pluggable architecture, where Lua scripts (referred to as ”plugins”) can be enabled and executed at runtime. Because of this, we like to think of Kong as a paragon of microservice architecture: at its core, it implements database abstraction, routing and plugin management. Plugins can live in separate code bases and be injected anywhere into the request lifecycle, all in a few lines of code.


![architecture](https://raw.githubusercontent.com/softasap/sa-kong/master/meta/kong-architecture.jpg "architecture")


Note: community version of the kong comes w/o any UI. You might want to consider some opensource WEBUI, like https://github.com/PGBI/kong-dashboard or https://github.com/pantsel/konga/.

Per our experience, https://github.com/PGBI/kong-dashboard uses more robust development and releasing processes, althouth konga looks more creatively.


```shell
# Install Kong Dashboard
npm install -g kong-dashboard

# Start Kong Dashboard
kong-dashboard start --kong-url http://kong:8001

# Start Kong Dashboard on a custom port
kong-dashboard start \
  --kong-url http://kong:8001 \
  --port [port]
```


```
  roles:
    - {
        role: "sa-kong"
      }
```

Advanced:

```
  roles:
    - {
        role: "sa-kong",
        kong_version: 0.12.1
      }
```



## Unsorted notes for future use.

Third party plugins you might be interested about

### kong-oidc

https://github.com/nokia/kong-oidc

kong-oidc is a plugin for Kong implementing the OpenID Connect Relying Party (RP) functionality.

It authenticates users against an OpenID Connect Provider using OpenID Connect Discovery and the Basic Client Profile (i.e. the Authorization Code flow).

It maintains sessions for authenticated users by leveraging lua-resty-openidc thus offering a configurable choice between storing the session state in a client-side browser cookie or use in of the server-side storage mechanisms shared-memory|memcache|redis.

It supports server-wide caching of resolved Discovery documents and validated Access Tokens.

In general you'll need an Authorization Server supporting OIDC with a registered client to start.
Here you can use either solutions like Keycloak/Gluu or those provided by third party (eg. Google's https://developers.google.com/identity/protocols/OpenIDConnect; in this case, you would use your Google account to login).

After you have the Client ID/secret and OIDC Discovery URL (see. https://auth0.com/docs/tutorials/openid-connect-discovery), you can enable the plugin.

Example curl could look like:

```sh
curl -XPOST -d 'name=oidc' -d 'config.client_id=<client_id>' -d 'config.client_secret =<client_secret>' -d 'config.discovery=<OIDC_Discovery_url>' http://kong:8001/plugins
```

After that, before accessing any APIs registered in Kong you will be redirected to the Authorization Server to login there.
This will also provide a SSO solution to all the APIs in Kong.


It makes Kong a OIDC Relying Party, so any API behind Kong can profit from the OIDC authentication protection without implementing the OIDC flows.

In practice it uses the Authorization Code grant (https://auth0.com/docs/api-auth/grant/authorization-code). If an unauthenticated user tries to access an API on Kong, on which this plugin is enabled it will redirect the User agent (browser) to the login page on the AS (AS location is set via discovery field in configuration). After successful login the AS gives you an access code and redirects back to Kong. Kong uses the access code to get the access, id and refresh token.

The tokens are stored in an encrypted session cookie. The encryption key is an combination of a few variables (user agent, remote ip address...) and the session_secret, which can be defined, when enabling the plugin (see https://github.com/nokia/kong-oidc/blob/master/kong/plugins/oidc/schema.lua). This field is optional, but highly recommended and has to be random!

If the Kong plugin sees, that there is already a cookie set, it will decrypt it and validate tokens. Refreshing of the access token using the refresh token is handled by this plugin also.

It also adds some information to the request for the upstream server. It sets the X-Userinfo header with the output from the Userinfo Endpoint (https://connect2id.com/products/server/docs/api/userinfo).

In general the OIDC flow and logic is implemented by the lua-resty-openidc package.

it's stateless, Kong datastore is not used. So if you would use this cookie in an another browser or from an another machine - it won't work.
To invalidate the tokens you can make a call to root url /logout (http://<kong_host>/logout). This will trigger a call to the OIDC End Session Endpoint.

The original tokens aren't send to the upstream server, but the X-Userinfo header contains claims from the ID token (but without AS signatures).


Process is stateless, Kong datastore is not used. So if you would use  cookie in an another browser or from an another machine - it won't work.
To invalidate the tokens you can make a call to root url /logout (http://<kong_host>/logout). This will trigger a call to the
OIDC End Session Endpoint.

The original tokens aren't send to the upstream server, but the X-Userinfo header contains claims from the ID token (but without AS signatures).



Side note - if you are going to use plugin in dockerized kong, you will need


```Dockerfile
FROM kong:1.4.0-alpine
LABEL description="Alpine + Kong 1.4.0 + kong-oidc plugin"
RUN apk update && apk add git unzip luarocks
RUN luarocks install kong-oidc
````

in image plugins can be activated using environment variable `KONG_PLUGINS`

```
KONG_PLUGINS=oidc
```

Example from kubernetes deployment

```yml

apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-kong
  annotations:
    plugins.konghq.com: oidc
spec:
  rules:
  - http:
      paths:
      - path: /graphql
        backend:
          serviceName: corphub-graphql-service
          servicePort: 8082
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: kong-oidc
  labels:
    global: "true"
config:
  client_id: kong
  client_secret: XXX
  discovery: http://keycloak:8180/auth/realms/master/.well-known/openid-configuration
plugin: oidc
```

### Kong Middleman

https://github.com/pantsel/kong-middleman-plugin

A Kong plugin that enables an extra HTTP POST request before proxying the original.

### kong-external-oauth

https://github.com/mogui/kong-external-oauth

A Kong plugin, that let you use an external Oauth 2.0 provider to protect your API.

```
$ luarocks install external-oauth
```

To make Kong aware that it has to look for the new plugin, you'll have to add it to the custom_plugins property in your configuration file.

```yml
custom_plugins:
    - external-oauth
```

You can add the plugin with the following request:

```
$ curl -X POST http://kong:8001/apis/{api}/plugins \
    --data "name=external-oauth" \
    --data "config.authorize_url=https://oauth.something.net/openid-connect/authorize" \
    --data "config.scope=openid+profile+email" \
    --data "config.token_url=https://oauth.something.net/openid-connect/token" \
    --data "config.client_id=SOME_CLEINT_ID" \
    --data "config.client_secret=SOME_SECRET_KEY" \
    --data "config.user_url=https://oauth.something.net/openid-connect/userinfo" \
    --data "config.user_keys=email,name,sub"
    --data "config.hosted_domain=mycompany.com"
    --data "config.email_key=email"
```


| Form Parameter | default | description |
| --- 						| --- | --- |
| `name` 					        | | plugin name `external-oauth` |
| `config.authorize_url` 	| | authorization url of the OAUTH provider (the one to which you will be redirected when not authenticated) |
| `config.scope` 			    | | OAUTH scope of the authorization request |
| `config.token_url` 		  | | url of the Oauth provider to request the access token |
| `config.client_id` 		  | | OAUTH Client Id |
| `config.client_secret` 	| | OAUTH Client Secret |
| `config.user_url` 		  | | url of the oauth provider used to retrieve user information and also check the validity of the access token |
| `config.user_keys` <br /> <small>Optional</small>		| `username,email` | keys to extract from the `user_url` endpoint returned json, they will also be added to the headers of the upstream server as `X-OAUTH-XXX` |
| `config.hosted_domain`  | | domain whose users must belong to in order to get logged in. Ignored if empty |
| `config.email_key` 		  | | key to be checked for hosted domain, taken from userinfo endpoint |
| `config.user_info_periodic_check` 		  | 60 | time in seconds between token checks |

In addition to the `user_keys` will be added a `X-OAUTH-TOKEN` header with the access token of the provider.

Postgres backend
----------------

pg_hba.conf after modifications will look similar to

```
local   all             postgres                                peer

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     md5
# local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            password
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
#local   replication     postgres                                peer
#host    replication     postgres        127.0.0.1/32            md5
#host    replication     postgres        ::1/128                 md5
```

Usage with ansible galaxy workflow
----------------------------------

If you installed the sa-kong  role using the command


`
   ansible-galaxy install softasap.sa-kong
`

the role will be available in the folder library/sa-kong

Please adjust the path accordingly.

```YAML

     - {
         role: "softasap.sa-kong"
       }

```


Copyright and license
---------------------

Code is dual licensed under the [BSD 3 clause] (https://opensource.org/licenses/BSD-3-Clause) and the [MIT License] (http://opensource.org/licenses/MIT). Choose the one that suits you best.

Reach us:

Subscribe for roles updates at [FB] (https://www.facebook.com/SoftAsap/)

Join gitter discussion channel at [Gitter](https://gitter.im/softasap)

Discover other roles at  http://www.softasap.com/roles/registry_generated.html

visit our blog at http://www.softasap.com/blog/archive.html
