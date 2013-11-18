#!/usr/bin/python

import subprocess
import sys
import json
from ..exceptions import *
from ..utils import DataHash
from ..conf.conffile import *
from persistence import BlockDevicePersistence
import storagecore

__author__="raltnoeder"
__date__ ="$Sep 12, 2013 10:49:42 AM$"


class LVM(object):
    KEY_DEV_PATH  = "dev-path"
    KEY_VG_NAME   = "volume-group"
    KEY_LVM_PATH  = "lvm-path"
    
    LVM_CONFFILE = "/etc/drbdmanaged-lvm.conf"
    LVM_SAVEFILE = "/var/lib/drbdmanage/drbdmanaged-lvm.local.json"
    
    LVM_CREATE   = "lvcreate"
    LVM_REMOVE   = "lvremove"
    LVM_LVS      = "lvs"
    
    CONF_DEFAULTS = {
      KEY_DEV_PATH : "/dev/mapper/",
      KEY_VG_NAME  : "drbdpool",
      KEY_LVM_PATH : "/sbin"
    }
    
    _lvs  = None
    _conf = None
    
    
    def __init__(self):
        try:
            self._lvs   = dict()
            conf_loaded = None
            try:
                self.load_state()
            except PersistenceException as p_exc:
                sys.stderr.write("lvm.LVM: Warning: Cannot load the LVM "
                  " state file: %s\n" % self.LVM_SAVEFILE)
            try:
                conf_loaded = self.load_conf()
            except IOError as io_err:
                sys.stderr.write("lvm.LVM: Warning: Cannot load the "
                  "LVM configuration file: %s\n" % self.LVM_CONFFILE)
            if conf_loaded is None:
                self._conf = self.CONF_DEFAULTS
            else:
                self._conf = ConfFile.conf_defaults_merge(self.CONF_DEFAULTS,
                  conf_loaded)
        except Exception as exc:
            print "DEBUG lvm.LVM: ", exc
    
    
    def create_blockdevice(self, name, id, size):
        bd = None
        lv_name = self._lv_name(name, id)
        try:
            if self._create_lv(lv_name, size) == 0:
                bd = storagecore.BlockDevice(lv_name, size,
                  self._lv_path_prefix() + lv_name)
                self._lvs[lv_name] = bd
                self.save_state()
        except Exception as exc:
            sys.stderr.write("DEBUG: LVM: create_blockdevice failed\n")
            print exc
        return bd
    
    
    def remove_blockdevice(self, blockdevice):
        # FIXME: this function should also return whether lvremove succeeded
        try:
            self._remove_lv(blockdevice.get_name())
            del self._lvs[blockdevice.get_name()]
        except KeyError:
            return DM_ENOENT
        self.save_state()
        return DM_SUCCESS
    
    
    def get_blockdevice(self, name, id):
        bd = None
        try:
            bd = self._lvs[self._lv_name(name, id)]
        except KeyError:
            pass
        return bd
    
    
    def up_blockdevice(self, blockdevice):
        return DM_SUCCESS
    
    
    def down_blockdevice(self, blockdevice):
        return DM_SUCCESS
    
    
    def update_pool(self, node):
        rc = 1
        poolsize = -1
        poolfree = -1
        
        lvs = self._lv_command_path(self.LVM_LVS)
        lvm_proc = None
        
        try:
            lvm_proc = subprocess.Popen([lvs, "--noheadings", "--nosuffix",
              "--units", "m", "--separator", ",", "--options",
              "vg_size,vg_free", self._conf[self.KEY_VG_NAME]], 0, lvs,
              stdout=subprocess.PIPE, close_fds=True)
            pool_str = lvm_proc.stdout.readline()
            if pool_str is not None:
                pool_str = pool_str.strip()
                idx = pool_str.find(",")
                if idx != -1:
                    size_str = pool_str[:idx]
                    free_str = pool_str[idx + 1:]
                    idx = size_str.find(".")
                    if idx != -1:
                        size_str = size_str[:idx]
                    idx = free_str.find(".")
                    if idx != -1:
                        free_str = free_str[:idx]
                    try:
                        poolsize = long(size_str)
                        poolfree = long(free_str)
                    except ValueError:
                        poolsize = -1
                        poolfree = -1
                    node.set_pool(poolsize, poolfree)
                    rc = 0
        finally:
            if lvm_proc is not None:
                try:
                    lvm_proc.stdout.close()
                except Exception:
                    pass
                lvm_proc.wait()
        return rc
    
    
    def _create_lv(self, name, size):
        # FIXME experimental/hardcoded
        lvcreate = self._lv_command_path(self.LVM_CREATE)
        
        lvm_proc = subprocess.Popen([lvcreate, "-n", name, "-L",
          str(size) + "m", self._conf[self.KEY_VG_NAME]], 0, lvcreate,
          close_fds=True
          ) # disabled: stdout=subprocess.PIPE
        rc = lvm_proc.wait()
        return rc
    
    
    def _remove_lv(self, name):
        # FIXME experimental/hardcoded
        lvm_dir = self._conf[self.KEY_LVM_PATH]
        if not lvm_dir.endswith("/"):
            lvm_dir += "/"
        lvremove = self._lv_command_path(self.LVM_REMOVE)
        
        lvm_proc = subprocess.Popen([lvremove, "--force",
          self._conf[self.KEY_VG_NAME] + "/" + name], 0, lvremove,
          close_fds=True
          ) # disabled: stdout=subprocess.PIPE
        rc = lvm_proc.wait()
        return rc
    
    
    def _lv_command_path(self, cmd):
        lvm_dir = self._conf[self.KEY_LVM_PATH]
        if not lvm_dir.endswith("/"):
            lvm_dir += "/"
        cmd_path = lvm_dir + cmd
        return cmd_path
    
    
    def _lv_name(self, name, id):
        return ("%s_%.2d" % (name, id));
    
    
    def _lv_path_prefix(self):
        vg_name  = self._conf[self.KEY_VG_NAME]
        dev_path = self._conf[self.KEY_DEV_PATH]
        if not dev_path.endswith("/"):
            lv_path_prefix = dev_path + "/" + vg_name + "-"
        else:
            lv_path_prefix = dev_path + vg_name + "-"
        return lv_path_prefix
        
    
    def load_conf(self):
        file = None
        conf = None
        try:
            file = open(self.LVM_CONFFILE, "r")
            conffile = ConfFile(file)
            conf = conffile.get_conf()
        except IOError as io_err:
            print io_err
        finally:
            if file is not None:
                file.close()
        return conf
    
    
    def load_state(self):
        file = None
        try:
            stored_hash = None
            file = open(self.LVM_SAVEFILE, "r")
            offset = 0
            line = file.readline()
            while len(line) > 0:
                if line.startswith("sig:"):
                    stored_hash = line[4:]
                    if stored_hash.endswith("\n"):
                        stored_hash = stored_hash[:len(stored_hash) - 1]
                    break
                else:
                    offset = file.tell()
                line = file.readline()
            file.seek(0)
            if offset != 0:
                load_data = file.read(offset)
            else:
                load_data = file.read()
            if stored_hash is not None:
                hash = DataHash()
                hash.update(load_data)
                computed_hash = hash.get_hex_hash()
                if computed_hash != stored_hash:
                    sys.stderr.write("Warning: configuration data does not "
                      "match its signature\n")
            lvm_con = json.loads(load_data)
            for properties in lvm_con.itervalues():
                bd = BlockDevicePersistence.load(properties)
                if bd is not None:
                    self._lvs[bd.get_name()] = bd
        except Exception as exc:
            raise PersistenceException
        finally:
            if file is not None:
                file.close()
    
    
    def save_state(self):
        print "DEBUG: save_state"
        lvm_con = dict()
        for bd in self._lvs.itervalues():
            bd_persist = BlockDevicePersistence(bd)
            bd_persist.save(lvm_con)
        file = None
        try:
            file = open(self.LVM_SAVEFILE, "w")
            hash = DataHash()
            save_data = json.dumps(lvm_con, indent=4, sort_keys=True) + "\n"
            hash.update(save_data)
            file.write(save_data)
            file.write("sig:" + hash.get_hex_hash() + "\n")
        except Exception as exc:
            raise PersistenceException
        finally:
            if file is not None:
                file.close()
    
    
    def reconfigure(self):
        pass
