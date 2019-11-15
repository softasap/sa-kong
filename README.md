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


Copyright and license
---------------------

Code is dual licensed under the [BSD 3 clause] (https://opensource.org/licenses/BSD-3-Clause) and the [MIT License] (http://opensource.org/licenses/MIT). Choose the one that suits you best.

Reach us:

Subscribe for roles updates at [FB] (https://www.facebook.com/SoftAsap/)

Join gitter discussion channel at [Gitter](https://gitter.im/softasap)

Discover other roles at  http://www.softasap.com/roles/registry_generated.html

visit our blog at http://www.softasap.com/blog/archive.html
