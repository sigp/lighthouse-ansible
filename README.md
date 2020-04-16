# lighthouse-ansible

[Ansible](https://www.ansible.com/) workspace for managing Lighthouse nodes.

This workspace is currently geared towards managing Amazon Linux nodes on AWS
EC2, however it could easily be made more generic.

## Goals

The goal of this Ansible workspace is to provision and manage Lighthouse
nodes. It supports two primary types of nodes:

- **Boot nodes**: runs a `lighthouse bn` process.
- **Validator clients**: runs `lighthouse bn`, `lighthouse vc` and
	`geth` processes.

These processes are run via the following three systemd units:

- [`lighthouse-bn.service`](./roles/lighthouse/templates/lighthouse-bn.service.j2):
  - Runs `lighthouse bn ...`
  - Data directory at `~/.lighthouse/beacon`.
  - Start with `systemctl start lighthouse-bn`.
  - Stop with `systemctl stop lighthouse-bn`.
  - Follow logs with `journalctl -f -u lighthouse-bn`
- [`lighthouse-vc.service`](./roles/lighthouse/templates/lighthouse-vc.service.j2):
  - Runs `lighthouse vc ...`
  - Data directory at `~/.lighthouse/validators`.
  - Start with `systemctl start lighthouse-vc`.
  - Stop with `systemctl stop lighthouse-vc`.
  - Follow logs with `journalctl -f -u lighthouse-vc`
- [`geth.service`](./roles/geth/templates/geth.service.j2):
  - Runs `geth ...`
  - Data directory at `~/.ethereum`.
  - Start with `systemctl start geth`.
  - Stop with `systemctl stop geth`.
  - Follow logs with `journalctl -f -u geth`


## Ansible Usage

The Ansible workspace is organised as per the [Roles Directory
Structure](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html).

### Inventory

The [`example-testnet`](./example-testnet) is an Ansible [Dynamic
Inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html)
using the [EC2 inventory source]
(https://docs.ansible.com/ansible/latest/plugins/inventory/aws_ec2.html).

Configure your own testnet by duplicating the `example-testnet` inventory.
Modify the `group_vars/all.yml` file to configure it. Be sure to use a
different `testnet_tag` for each testnet, so you can maintain independent
control. Don't forget to update the `tag:Testnet` filter in
`hosts.aws_ec2.yml`!

### Secrets

As with most infrastructure, there are secrets you should keep locally and not
add to the repository. These secret variables are expected to be found in a
`secret.yml` file in the root of the repository. A
[example-secret.yml](./example-secret.yml) file is included to indicate what is
required.

Additionally, you should have the `AWS_ACCESS_KEY` and `AWS_SECRET_KEY`
environment variables set.

### Roles

There are several Ansible [roles](./roles), each providing functionality for a
different service:

- [`common`](./roles/common): provides common variables (required by most roles).
- [`aws`](./roles/asws): provides tasks for managing AWS infrastructure.
- [`geth`](./roles/geth): provides tasks for managing Geth.
- [`lighthouse`](./roles/lighthouse): provides tasks for managing Lighthouse.
- [`rust`](./roles/rust): provides tasks for installing and upgrading Rust.


### Plays

[Playbooks](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html)
("plays") are collections of tasks that are run against nodes in an inventory.

Playbooks are run using the `ansible-playbook` CLI command. Here's an example:

```shell
ansible-playbook -i example-testnet infrastructure.yml
```

This command will deploy all the infrastructure defined in `example-testnet`
(some security groups and EC2 instances). Check to see that nodes were deployed
with `ansible-inventory -i example-testnet/ --graph`.

#### List of Plays

Each play is listed here:
 - [infrastructure.yml](./infrastructure.yml): deploys or updates the AWS infrastructure that forms the hosts.
 - [packages.yml](./packages.yml): deploys or updates packages and configuration on hosts created by the above play.
 - [kill-infrastructure.yml](./kill-infrastructure.yml): terminates all the running infrastructure (use with caution).
