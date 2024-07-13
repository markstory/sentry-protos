import dataclasses
import glob
import json
import os.path
from os import path
from typing import Iterator, Any, TypeVar

from jinja2 import Environment, FileSystemLoader, select_autoescape
from openapi_pydantic import Schema, Reference, DataType

_T = TypeVar("_T")

here = path.abspath(path.dirname(__file__))

jinja_env = Environment(
    loader=FileSystemLoader(here),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
    line_statement_prefix="#",
)
jinja_env.add_extension('jinja2.ext.do')
jinja_env.globals['len'] = len

def register_filter(c: _T) -> _T:
    jinja_env.filters[c.__name__] = c
    return c

def register_global(c: _T) -> _T:
    jinja_env.globals[c.__name__] = c
    return c

def register_test(c: _T) -> _T:
    jinja_env.tests[c.__name__] = c
    return c


def cleaneup_jsonschema(d: Any) -> dict:
    """
    Converts a jsonschema to an openapi schema to make it easier to operate on, normalizing
    some of the weirder jsonschema options where possible.
    """

    if isinstance(d, bool):
        d = {}

    if '$ref' in d:
        return d

    if 'definitions' in d:
        for k, v in d['definitions'].items():
            d['definitions'][k] = cleaneup_jsonschema(v)

    if 'type' in d and isinstance(d['type'], list):
        if len(d['type']) == 1:
            d['type'] = d['type'][0]

    if 'anyOf' in d:
        d['anyOf'] = [cleaneup_jsonschema(v) for v in d['anyOf']]

    if 'items' in d:
        if isinstance(d['items'], list):
            d['prefixItems'] = [cleaneup_jsonschema(v) for v in d['items']]
            del d['items']
        else:
            d['items'] = cleaneup_jsonschema(d['items'])

    if 'properties' in d:
        for k, v in d['properties'].items():
            d['properties'][k] = cleaneup_jsonschema(v)

    if 'additionalProperties' in d and isinstance(d['additionalProperties'], dict):
        d['additionalProperties'] = cleaneup_jsonschema(d['additionalProperties'])

    return d

@register_global
@dataclasses.dataclass
class NamedStructureType:
    definition_dependencies: "list[str]"
    properties: "dict[str, NamedSchema]"
    definitions: dict[str, Schema] = dataclasses.field(repr=False)

@register_global
@dataclasses.dataclass
class ScalarType:
    data_type: DataType | None = None
    format: str | None = None
    well_known_type: str | None = None

    @property
    def proto_scalar_type(self) -> str:
        if self.format:
            if self.format in {'uint64', 'uint32', 'int32', 'int64', 'double'}:
                return self.format
            elif self.format in {"uuid"}:
                return "string"
            else:
                raise RuntimeError(f"Unsupported property format: {self.format}")
        if self.data_type:
            if self.data_type == DataType.STRING:
                return "string"
            elif self.data_type == DataType.NUMBER:
                return "double"
            elif self.data_type == DataType.INTEGER:
                return "int64"
            elif self.data_type == DataType.BOOLEAN:
                return "bool"
        elif self.well_known_type:
            return "google.protobuf.Value"

        raise RuntimeError(f"Unsupported type: {self!r}")

_any = ScalarType(well_known_type="google.protobuf.Value")
_struct = ScalarType(well_known_type="google.protobuf.Struct")
_list = ScalarType(well_known_type="google.protobuf.ListValue")

@register_global
@dataclasses.dataclass
class MapType:
    inner: ScalarType | NamedStructureType

@register_global
@dataclasses.dataclass
class RepeatedType:
    inner: ScalarType | NamedStructureType

@register_global
@dataclasses.dataclass
class NullableType:
    inner: ScalarType | NamedStructureType
    definitions: dict[str, Schema] = dataclasses.field(repr=False)

@register_global
@dataclasses.dataclass
class SumType:
    parts: "list[NamedSchema]"

@dataclasses.dataclass
class NamedSchema:
    """
    Wrapper that gets injected into the jinja2 template, provides utilities that operate on the schema.
    """
    name: str
    schema: Schema
    definitions: dict[str, Schema]
    required: bool = False

    def __repr__(self):
        return f"NamedSchema(name={self.name!r}, unpacked={self.unpack()!r}, required={self.required!r})"

    def resolve(self, schema_or_ref: Schema | Reference) -> Schema:
        if isinstance(schema_or_ref, Reference):
            if not schema_or_ref.ref.startswith("#/definitions/"):
                raise RuntimeError(f"Unsupported reference: {schema_or_ref.ref!r}")
            type_name = schema_or_ref.ref.split("/")[-1]
            return self.definitions[type_name]
        return schema_or_ref

    def unpack(self) -> NamedStructureType | ScalarType | NullableType | RepeatedType | MapType | SumType:
        inner_nullable: Schema | None = None
        if self.schema.anyOf is not None and len(self.schema.anyOf) == 2 and self.schema.anyOf[1].type == DataType.NULL:
            inner_nullable = self.resolve(self.schema.anyOf[0])

        if isinstance(self.schema.type, list):
            if DataType.NULL == self.schema.type[1] and len(self.schema.type) == 2:
                inner_nullable = self.schema.copy()
                inner_nullable.type = self.schema.type[0]

        if inner_nullable is not None:
            unpacked = dataclasses.replace(self, schema=inner_nullable).unpack()
            while isinstance(unpacked, NullableType):
                unpacked = unpacked.inner

            if self.required:
                return unpacked
            if isinstance(unpacked, (RepeatedType, MapType, SumType)):
                return unpacked
            return NullableType(inner=unpacked, definitions=self.definitions)

        if self.schema.anyOf and len(self.schema.anyOf) == 1:
            return dataclasses.replace(self, schema=self.resolve(self.schema.anyOf[0])).unpack()

        if self.schema.anyOf:
            parts: list[NamedSchema] = []
            for part in self.schema.anyOf:
                if isinstance(part, Reference):
                    name = part.ref.split("/")[-1].lower()
                    parts.append(NamedSchema(name=name, schema=self.resolve(part), definitions=self.definitions))
                else:
                    return _any
            return SumType(parts)

        inner_repeated: Schema | None = None
        if self.schema.type is not None and self.schema.type == DataType.ARRAY:
            if self.schema.prefixItems:
                return _list
            if not self.schema.items:
                raise RuntimeError(f"Unsupported data type: {self.schema}")
            inner_repeated = self.resolve(self.schema.items)

        if inner_repeated is not None:
            unpacked = dataclasses.replace(self, schema=inner_repeated).unpack()
            while isinstance(unpacked, NullableType):
                unpacked = unpacked.inner
            if isinstance(unpacked, (RepeatedType, MapType, SumType)):
                return _list

            return RepeatedType(unpacked)

        inner_map: Schema | None = None
        if self.schema.type == DataType.OBJECT and not self.schema.properties and isinstance(self.schema.additionalProperties, (Reference, Schema)):
            inner_map = self.resolve(self.schema.additionalProperties)

        if inner_map is not None:
            unpacked = dataclasses.replace(self, schema=inner_map).unpack()
            while isinstance(unpacked, NullableType):
                unpacked = unpacked.inner

            if isinstance(unpacked, (RepeatedType, MapType, SumType)):
                return _struct

            return MapType(unpacked)

        if self.schema.type == DataType.OBJECT:
            if self.schema.properties:
                result = NamedStructureType(definition_dependencies=[], properties={}, definitions=self.definitions)
                for key, value in self.schema.properties.items():
                    if not key.isidentifier():
                        return _struct
                    named = result.properties[key] = NamedSchema(
                        name="",
                        schema=self.resolve(value),
                        definitions=self.definitions,
                        required=self.schema.required and key in self.schema.required,
                    )
                    if isinstance(value, Reference):
                        named.name = value.ref.split("/")[-1]
                    else:
                        named.name =f"{self.name}_{key}"
                        result.definition_dependencies.append(key)
                return result
            return _struct

        if self.schema.type in (DataType.STRING, DataType.NUMBER, DataType.INTEGER, DataType.BOOLEAN, DataType.NUMBER):
            return ScalarType(self.schema.type, self.schema.schema_format)

        return _any


@dataclasses.dataclass
class TopLevelSchema:
    package_name: str
    schema: Schema

    @property
    def schemas(self) -> "Iterator[NamedSchema]":
        definitions = {k: Schema.model_validate(v) for k, v in self.schema.__pydantic_extra__.get('definitions', {}).items()}
        yield NamedSchema(self.schema.title, self.schema, definitions)

        for k, v in definitions.items():
            yield NamedSchema(k, Schema.model_validate(v), definitions)

@register_test
def an(obj: Any, kind: Any):
    return isinstance(obj, kind)

@register_global
def raise_helper(*parts: Any):
    raise RuntimeError(" ".join(str(p) for p in parts))

@register_filter
def as_comment(value: str | None) -> str:
    if value is None: return ''
    return "/*\n" + value.strip() + "\n*/"

def main():
    src_root = os.path.abspath(os.path.join(here, ".."))
    print(f"Searching for protos in {src_root}...")
    for src in glob.glob(f"{src_root}/**/*.schema.json"):
        dst = src.replace(".schema.json", ".proto")
        with open(src, "r") as source_schema, open(dst, "w") as output_proto:
            print(f"Processing {src}")
            d = json.load(source_schema)
            d = cleaneup_jsonschema(d)

            schema = TopLevelSchema(
                "sentry_protos." + os.path.relpath(src, src_root).replace("/", ".").removesuffix(".schema.json"),
                                    Schema.model_validate(d))

            print(f"Writing {dst}...")
            output_proto.write(
                jinja_env.get_template("js2.proto.jinja").render(top_level=schema)
            )
