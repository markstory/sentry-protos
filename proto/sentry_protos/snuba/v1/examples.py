from datetime import datetime
from sentry_protos.snuba.v1.endpoint_time_series_pb2 import (
    TimeSeriesRequest,
    AttributeAggregation,
    TimeSeries,
    TimeSeriesResponse,
    Function,
)
from sentry_protos.snuba.v1.trace_item_attribute_pb2 import AttributeKey, AttributeValue
from sentry_protos.snuba.v1.endpoint_trace_item_attributes_pb2 import (
    TraceItemAttributeNamesRequest,
    TraceItemAttributeNamesResponse,
    TraceItemAttributeValuesRequest,
    TraceItemAttributeValuesResponse,
)
from sentry_protos.snuba.v1.request_common_pb2 import RequestMeta, TraceItemName
from google.protobuf.timestamp_pb2 import Timestamp


COMMON_META = RequestMeta(
    project_ids=[1, 2, 3],
    organization_id=1,
    cogs_category="something",
    referrer="something",
    start_timestamp=Timestamp(seconds=int(datetime(2024, 4, 20, 16, 20).timestamp())),
    end_timestamp=Timestamp(seconds=int(datetime(2024, 4, 20, 17, 20).timestamp())),
    trace_item_name=TraceItemName.TRACE_ITEM_NAME_EAP_SPANS,
)


def test_example_time_series():
    TimeSeriesRequest(
        meta=COMMON_META,
        aggregations=[
            AttributeAggregation(
                aggregate=Function.FUNCTION_AVG,
                key=AttributeKey(type=AttributeKey.TYPE_FLOAT, name="sentry.duration"),
                label="p50",
            ),
            AttributeAggregation(
                aggregate=Function.FUNCTION_P95,
                key=AttributeKey(type=AttributeKey.TYPE_FLOAT, name="sentry.duration"),
                label="p90",
            ),
        ],
        granularity_secs=60,
        group_by=[
            AttributeKey(type=AttributeKey.TYPE_STRING, name="endpoint_name"),
            AttributeKey(type=AttributeKey.TYPE_STRING, name="consumer_group"),
        ],
    )

    TimeSeriesResponse(
        result_timeseries=[
            TimeSeries(
                label="p50",
                group_by_attributes={
                    "endpoint_name": "/v1/rpc",
                    "consumer_group": "snuba_outcomes_consumer",
                },
                data_points=[42 for _ in range(60)],
                num_events=1337,
                avg_sampling_rate=0.1,
            ),
            TimeSeries(
                label="p50",
                group_by_attributes={
                    "endpoint_name": "/v2/rpc",
                    "consumer_group": "snuba_outcomes_consumer",
                },
                data_points=[42 for _ in range(60)],
                num_events=1337,
                avg_sampling_rate=0.1,
            ),
            TimeSeries(
                label="p90",
                group_by_attributes={
                    "endpoint_name": "/v1/rpc",
                    "consumer_group": "snuba_outcomes_consumer",
                },
                data_points=[42 for _ in range(60)],
                num_events=1337,
                avg_sampling_rate=0.1,
            ),
            TimeSeries(
                label="p90",
                group_by_attributes={
                    "endpoint_name": "/v2/rpc",
                    "consumer_group": "snuba_outcomes_consumer",
                },
                data_points=[42 for _ in range(60)],
                num_events=1337,
                avg_sampling_rate=0.1,
            ),
        ]
    )
