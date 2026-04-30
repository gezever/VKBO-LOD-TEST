# Run with: locust -f tests/performance/locustfile.py --host https://data.vlaanderen.be
from locust import HttpUser, between, task


class VkboLodUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def deref_vestiging(self):
        self.client.get(
            "/id/vestiging/2311823764",
            headers={"Accept": "text/turtle"},
            name="/id/vestiging/[id]",
        )

    @task(1)
    def deref_onderneming(self):
        self.client.get(
            "/id/onderneming/0401050557",
            headers={"Accept": "text/turtle"},
            name="/id/onderneming/[id]",
        )
