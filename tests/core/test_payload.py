import unittest

# project
from checks.collector import AgentPayload

# 3p
from mock import Mock


class TestAgentPayload(unittest.TestCase):
    """
    Test the agent payload logic
    """
    def test_add_rem_elem(self):
        """
        Can set, read, update and delete data in the payload
        """
        payload = AgentPayload()

        # Is initially empty
        self.assertEquals(len(payload), 0)

        # Set a new value
        payload['something'] = "value"
        self.assertEquals(len(payload), 1)

        # Can access it
        self.assertEquals(payload['something'], "value")

        # Can update it
        payload['something'] = "other value"
        self.assertEquals(len(payload), 1)
        self.assertEquals(payload['something'], "other value")

        # Delete it
        del payload['something']
        self.assertEquals(len(payload), 0)

    def test_split_metrics_and_meta(self):
        """
        Split data and metadata payloads. Submit to the right endpoint.
        """
        # Some not metadata keys
        DATA_KEYS = ['key1', 'key2', 'key3', 'key4']

        payload = AgentPayload()

        # Adding metadata values
        for key in AgentPayload.METADATA_KEYS:
            payload[key] = "value"
        len_payload1 = len(payload)
        self.assertEquals(len_payload1, len(AgentPayload.METADATA_KEYS))
        self.assertEquals(len_payload1, len(payload.payload_meta))
        self.assertEquals(len(payload.payload_data), 0)

        # Adding data values
        for key in DATA_KEYS:
            payload[key] = "value"
        len_payload2 = len(payload)
        self.assertEquals(len_payload2, len_payload1 + len(DATA_KEYS))
        self.assertEquals(len_payload2 - len_payload1, len(payload.payload_data))
        self.assertEquals(len(payload.payload_meta), len_payload1)

        # Adding common values
        for key in AgentPayload.DUPLICATE_KEYS:
            payload[key] = "value"
        len_payload3 = len(payload)
        self.assertEquals(len_payload3, len_payload2 + 2 * len(AgentPayload.DUPLICATE_KEYS))
        self.assertEquals(len_payload1 + len(AgentPayload.DUPLICATE_KEYS),
                          len(payload.payload_meta))
        self.assertEquals(len_payload2 - len_payload1 + len(AgentPayload.DUPLICATE_KEYS),
                          len(payload.payload_data))

    def test_emit_payload(self):
        """
        Submit each payload to its specific endpoint.
        """
        payload = AgentPayload()

        fake_emitter = Mock()
        fake_emitter.__name__ = None
        payload.emit(None, None, [fake_emitter], True)
        fake_emitter.assert_any_call(payload.payload_data, None, None, "metrics")
        fake_emitter.assert_any_call(payload.payload_meta, None, None, "metadata")
