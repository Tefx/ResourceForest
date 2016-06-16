from random import choice, randint

from faker import Factory

from hierarchical import ResourceTree


def make_fake_tree(n_project, n_version, n_purpose, n_user_per_purpose,
                   n_person, n_user_per_person,
                   n_host, n_user_per_host):
    root_tree = ResourceTree()
    faker = Factory.create("zh_CN")

    root_tree.create("/hosts", "ResourceTree")
    user_resource_pool = []
    for _ in range(n_host):
        ip = faker.ipv4()
        root_tree.create("/hosts/{}".format(ip), "Host",
                         os=choice(["Linux", "AIX", "HP-UX", "Salaries"]),
                         memory=choice(["24GB", "12GB", "56GB"]),
                         cpu=choice(["Intel 2.5GHz", "Power 3.6GHz"]),
                         disk=choice(["240GB", "500GB", "2TB"]))
        for _ in range(n_user_per_host):
            username = faker.word()
            scheme = choice(["ssh", "telnet", "oracle", "mysql"])
            if scheme in ["ssh", "telnet"]:
                port = randint(100, 200)
                in_path = ""
            else:
                port = randint(10000, 20000)
                in_path = "/{}".format(faker.word()[:2])

            path = "/hosts/{}/{}".format(ip, username)
            user_resource_pool.append(path)

            root_tree.create(path, "User",
                             scheme=scheme,
                             port=port,
                             in_path=in_path,
                             password=faker.password())

    root_tree.create("/persons", "ResourceTree")
    for _ in range(n_person):
        name = faker.name()
        root_tree.create("/persons/{}".format(name), "Person")
        for _ in range(n_user_per_person):
            user = choice(user_resource_pool)
            root_tree.link("/persons/{}/".format(name), user)

    root_tree.create("/projects", "ResourceTree")
    for _ in range(n_project):
        project = faker.country()
        root_tree.create("/projects/{}".format(project), "Project")
        for _ in range(n_version):
            version = "v{}".format(randint(22, 75))
            root_tree.create("/projects/{}/{}".format(project, version), "Version")
            for _ in range(n_purpose):
                purpose = faker.job()
                root_tree.create("/projects/{}/{}/{}".format(project, version, purpose), "Purpose")
                for _ in range(n_user_per_purpose):
                    user = choice(user_resource_pool)
                    root_tree.link("/projects/{}/{}/{}/".format(project, version, purpose), user)

    return root_tree


if __name__ == '__main__':
    # rt = make_fake_tree(n_project=50, n_version=10, n_purpose=5, n_user_per_purpose=2,
    #                     n_person=100, n_user_per_person=20,
    #                     n_host=400, n_user_per_host=10)

    rt = make_fake_tree(n_project=5, n_version=2, n_purpose=3, n_user_per_purpose=1,
                        n_person=10, n_user_per_person=3,
                        n_host=4, n_user_per_host=5)
    # print(rt.tree())
