import docker
import time

client = docker.from_env()
image_name = "elective-app"
container_base_name = "app"
port_base = 5001
cpu_threshold = 50
max_containers = 5

# Keep track of containers already created
created_containers = set()

# Detect existing containers at start
for c in client.containers.list():
    if c.name.startswith(container_base_name):
        created_containers.add(c.name)

def get_container_cpu_percent(container_name):
    try:
        container = client.containers.get(container_name)
        stats = container.stats(stream=False)

        cpu_stats = stats["cpu_stats"]
        precpu_stats = stats["precpu_stats"]

        cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - precpu_stats["cpu_usage"]["total_usage"]
        system_delta = cpu_stats["system_cpu_usage"] - precpu_stats["system_cpu_usage"]

        num_cpus = len(cpu_stats["cpu_usage"].get("percpu_usage", [])) or 1

        if system_delta > 0.0 and cpu_delta > 0.0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
            return round(cpu_percent, 2)
    except Exception as e:
        print(f"Error reading stats for {container_name}: {e}")
    return 0.0

def get_next_port():
    return port_base + len(created_containers)

def scale():
    active_apps = [c.name for c in client.containers.list() if c.name.startswith(container_base_name)]
    if not active_apps:
        print("No running app containers found.")
        return

    for app in active_apps:
        cpu = get_container_cpu_percent(app)
        print(f"{app} CPU usage: {cpu}%")

        if cpu > cpu_threshold and len(created_containers) < max_containers:
            next_id = len(created_containers) + 1
            next_port = get_next_port()
            new_name = f"{container_base_name}{next_id}"

            print(f"Spawning new container: {new_name} on port {next_port}")
            client.containers.run(
                image_name,
                name=new_name,
                ports={"5001/tcp": next_port},
                environment={"VIRTUAL_HOST": "localhost"},
                detach=True
            )
            created_containers.add(new_name)
            break  # Add one at a time

if __name__ == "__main__":
    while True:
        scale()
        time.sleep(1)
