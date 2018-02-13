sa-kong
=======

[![Build Status](https://travis-ci.org/softasap/sa-kong.svg?branch=master)](https://travis-ci.org/softasap/sa-kong)


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



Copyright and license
---------------------

Code is dual licensed under the [BSD 3 clause] (https://opensource.org/licenses/BSD-3-Clause) and the [MIT License] (http://opensource.org/licenses/MIT). Choose the one that suits you best.

Reach us:

Subscribe for roles updates at [FB] (https://www.facebook.com/SoftAsap/)

Join gitter discussion channel at [Gitter](https://gitter.im/softasap)

Discover other roles at  http://www.softasap.com/roles/registry_generated.html

visit our blog at http://www.softasap.com/blog/archive.html
