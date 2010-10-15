#!/usr/bin/env python

from starcluster import config
from starcluster import cluster
from starcluster import optcomplete
from starcluster.logger import log

from base import CmdBase


class CmdSshNode(CmdBase):
    """
    sshnode <cluster> <node>

    SSH to a cluster node

    Examples:

        $ starcluster sshnode mycluster master
        $ starcluster sshnode mycluster node001
        ...

    or same thing in shorthand:

        $ starcluster sshnode mycluster 0
        $ starcluster sshnode mycluster 1
        ...
    """
    names = ['sshnode', 'sn']

    @property
    def completer(self):
        if optcomplete:
            try:
                cfg = config.StarClusterConfig().load()
                ec2 = cfg.get_easy_ec2()
                cm = cluster.ClusterManager(cfg, ec2)
                clusters = cm.get_cluster_security_groups()
                compl_list = [cm.get_tag_from_sg(sg.name) \
                              for sg in clusters]
                max_num_nodes = 0
                for scluster in clusters:
                    num_instances = len(scluster.instances())
                    if num_instances > max_num_nodes:
                        max_num_nodes = num_instances
                compl_list.extend(['master'])
                compl_list.extend([str(i) for i in range(0, num_instances)])
                compl_list.extend(["node%03d" % i \
                                   for i in range(1, num_instances)])
                return optcomplete.ListCompleter(compl_list)
            except Exception, e:
                print e
                log.error('something went wrong fix me: %s' % e)

    def addopts(self, parser):
        parser.add_option("-u", "--user", dest="user", action="store",
                          type="string", default='root',
                          help="login as USER (defaults to root)")

    def execute(self, args):
        if len(args) != 2:
            self.parser.error(
                "please specify a <cluster> and <node> to connect to")
        scluster = args[0]
        ids = args[1:]
        for id in ids:
            self.cm.ssh_to_cluster_node(scluster, id, user=self.opts.user)