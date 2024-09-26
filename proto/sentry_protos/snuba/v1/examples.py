from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp
from sentry_protos.snuba.v1.endpoint_time_series_pb2 import (
    TimeSeries,
    TimeSeriesRequest,
    TimeSeriesResponse,
)
from sentry_protos.snuba.v1.endpoint_trace_item_attributes_pb2 import (
    TraceItemAttributeNamesRequest,
    TraceItemAttributeNamesResponse,
    TraceItemAttributeValuesRequest,
    TraceItemAttributeValuesResponse,
)
from sentry_protos.snuba.v1.endpoint_trace_item_table_pb2 import (
    Column,
    TraceItemColumnValues,
    TraceItemTableRequest,
    TraceItemTableResponse,
)
from sentry_protos.snuba.v1.request_common_pb2 import (
    RequestMeta,
    TraceItemName,
    PageToken,
)
from sentry_protos.snuba.v1.trace_item_filter_pb2 import (
    TraceItemFilter,
    ComparisonFilter,
    ExistsFilter,
    AndFilter,
    OrFilter,
)
from sentry_protos.snuba.v1.trace_item_attribute_pb2 import (
    AttributeAggregation,
    AttributeKey,
    AttributeValue,
    Function,
)

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
                buckets=[COMMON_META.start_timestamp for _ in range(60)],
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
                buckets=[COMMON_META.start_timestamp for _ in range(60)],
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
                buckets=[COMMON_META.start_timestamp for _ in range(60)],
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
                buckets=[COMMON_META.start_timestamp for _ in range(60)],
                data_points=[42 for _ in range(60)],
                num_events=1337,
                avg_sampling_rate=0.1,
            ),
        ]
    )


def test_example_table() -> None:
    TraceItemTableRequest(
        meta=COMMON_META,
        columns=[
            Column(
                key=AttributeKey(
                    type=AttributeKey.TYPE_STRING, name="sentry.span_name"
                ),
                label="span_name",
            ),
            Column(
                key=AttributeKey(type=AttributeKey.TYPE_FLOAT, name="sentry.duration"),
                label="duration",
            ),
        ],
        filter=TraceItemFilter(
            or_filter=OrFilter(
                filters=[
                    TraceItemFilter(
                        comparison_filter=ComparisonFilter(
                            key=AttributeKey(
                                type=AttributeKey.TYPE_STRING,
                                name="eap.measurement",
                            ),
                            op=ComparisonFilter.OP_LESS_THAN_OR_EQUALS,
                            value=AttributeValue(val_float=101),
                        ),
                    ),
                    TraceItemFilter(
                        comparison_filter=ComparisonFilter(
                            key=AttributeKey(
                                type=AttributeKey.TYPE_STRING,
                                name="eap.measurement",
                            ),
                            op=ComparisonFilter.OP_GREATER_THAN,
                            value=AttributeValue(val_float=999),
                        ),
                    ),
                ]
            )
        ),
        order_by=[
            TraceItemTableRequest.OrderBy(
                column=Column(
                    key=AttributeKey(
                        type=AttributeKey.TYPE_FLOAT, name="sentry.duration"
                    )
                )
            )
        ],
        limit=100,
    )

    TraceItemTableResponse(
        column_values=[
            TraceItemColumnValues(
                attribute_name="span_name",
                results=[AttributeValue(val_str="xyz"), AttributeValue(val_str="abc")],
            ),
            TraceItemColumnValues(
                attribute_name="duration",
                results=[AttributeValue(val_float=4.2), AttributeValue(val_float=6.9)],
            ),
        ],
        page_token=PageToken(
            filter_offset=TraceItemFilter(
                comparison_filter=ComparisonFilter(
                    key=AttributeKey(
                        type=AttributeKey.TYPE_FLOAT, name="sentry.duration"
                    ),
                    op=ComparisonFilter.OP_GREATER_THAN_OR_EQUALS,
                    value=AttributeValue(val_float=6.9),
                )
            )
        ),
    )
