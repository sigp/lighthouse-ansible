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

## Starting a testnet

In this example we're going to start a new testnet called "unity-4k".

_Note: don't use hypens in testnet names. Ansible does not enjoy that._

### 1. Define Inventory

Create a new inventory directory by copying an existing one (e.g., `example-testnet`):

```bash
cp -r example-testnet/ unity-4k
```

The _testnet tag_ uniquely indentifies testnet infrastructure and
configuration. It is an error to create two tesnets with the same testnet tag.
Ensure the testnet tag is changed in the following parts of the new inventory.
Ensure you replace `exampletestnet` with `unity-4k` in:

- The `tag:Testnet` field in `unity-4k/hosts.aws_ec2.yml`
- The `testnet_tag` var in `unity-4k/group_vars/all.yml`

Then, configure your testnet parameters in `unity-4k/group_vars/all.yml`. In
this testnet we want to have 4,096 validators at genesis, spread across 4 AWS
regions where each region has 2 VC+BN hosts and 2 "boot nodes" that are just
running a BN (16 nodes in total).

So, we'll set:

- `min_genesis_active_validator_count: 4096`
- `public_node_regions: ["ap-southeast-1", "eu-central-1", "us-west-2", "ap-south-1"]`
- `beacon_node_per_region: 0`
- `boot_node_per_region: 2`
- `validator_per_region: 2`

To ensure an even split of validators at genesis, also set:

- `validators_per_host: 512`

Since I added three new regions, I also need to reflect this in the `regions`
list in `unity-4k/hosts.aws_ec2.yml`:

```yaml
regions:
  - ap-southeast-1
  - eu-central-1
  - us-west-2
  - ap-south-1
```

### 2. Deploy infrastructure

Now the testnet is defined, we can actually create the infrastructure on AWS with:

```bash
ansible-playbook -i unity-4k infrastructure.yml
```

This command will create EC2 security groups and provision EC2 instances across
all regions.

### 2. Provision software packages

With the infrastructure now in place, we can install Lighthouse, Geth and the other required software.

```bash
ansible-playbook -i unity-4k -f 17 packages.yml
```

This command will do a lot of compilation, expect to take quite a while (minutes to hours).

Note: I have used `-f 17` to [set the number of parallel
processes](https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html#id2).
I know this testnet has 17 instances (16 nodes + 1 metrics server), so this
should ensure they build in parallel.
