# lighthouse-ansible

[Ansible](https://www.ansible.com/) workspace for managing Lighthouse nodes.

This workspace is currently geared towards managing Amazon Linux nodes on AWS
EC2, however it could easily be made more generic.

## Goals

The goal of this Ansible workspace is to provision and manage Lighthouse
nodes. It supports two primary types of nodes:

- **Boot nodes**: runs a `lighthouse bn` process.
- **Validator clients**: runs `lighthouse bn` and `lighthouse vc` processes and
	also a `geth` process.

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

The list of managed hosts is included in an
[Inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html);
we provide a [`example-inventory`](./example-inventory), however users will
likely generate their own inventories per testnet (e.g., `testnet5`).

Hosts are assigned to groups:

- `validators`: nodes which should run the `lighthouse-bn` and `lighthouse-vc`
	services.
- `boot_nodes`: nodes which should run a `lighthouse bn` service.
- `geth`: nodes which should run a `geth` service.


### Roles

There are several Ansible [roles](./roles), each providing functionality for a
different service:

- [`common`](./roles/common): provides common variables (required by most roles).
- [`geth`](./roles/geth): provides tasks for managing Geth.
- [`lighthouse`](./roles/lighthouse): provides tasks for managing Lighthouse.
- [`rust`](./roles/rust): provides tasks for installing and upgrading Rust.


### Plays

[Playbooks](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html)
("plays") are collections of tasks that are run against nodes in an inventory.

Playbooks are run using the `ansible-playbook` CLI command. Here's an example:

```shell
ansible-playbook -i testnet5 -l oregon migrate-from-docker-setup.yml
```

This command will use the `testnet5` inventory file (`-i`) to find hosts, the
action will be limited (`-l`) to nodes in the `oregon` group and it will run
the tasks in the `migrate-from-docker-setup.yml`.
