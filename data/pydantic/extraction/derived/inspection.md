# Extracted evidence inspection

Status: mechanically verified extraction; all applicability is pending human review.
No queries or gold labels exist. Quoted outputs are upstream text, never executed here.

```json
{
  "by_primary_document_snapshot": {
    "1.10.13": 14,
    "2.5.3": 20
  },
  "by_primary_source_type": {
    "conceptual_guide": 26,
    "migration_guide": 8
  },
  "compound_units": 11,
  "contributing_physical_sources": 20,
  "contributing_source_types": {
    "conceptual_guide": 8,
    "documentation_example": 11,
    "migration_guide": 1
  },
  "exact_duplicate_content_groups": [],
  "migration_share": 0.23529411764705882,
  "migration_units": 8,
  "pending_human_review": 34,
  "single_source_units": 23,
  "total_units": 34,
  "unknown_applicability_units": []
}
```

## Selection coverage and limitations

- No approved topic omitted. The source allowlist is narrowed where selection notes exclude helper siblings and unrelated configuration entries.
- models_parse.py: omit pickle/Path imports and all parse_raw/parse_file/file-writing code; only lines 2 and 5-20 contribute.
- Metadata headings outside selected body spans are retained only as heading ancestry, never copied into content.
- No standalone common-type subclass passage, generated API pages, or additional documentation included.
- All applicability annotations are proposals pending human review, not gold labels or independent behavioral verification.
- V1 nested-subclass behavior is retrospective evidence in the v2 snapshot; it is not asserted as a v1 source passage.
- Original documentation links and MkDocs admonitions/API references are retained as text; no link resolution or site rendering.
- Some approved examples contain incidental APIs. Their text is preserved without expanding evaluation topics.

## migration-config

Evidence ID: `evidence:883046956d69fc69fa76cd3a28d772a46f067d517f5d679bb3e3a6dfcc7b3383`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
### Changes to config

* In Pydantic V2, to specify config on a model, you should set a class attribute called `model_config` to be a dict
  with the key/value pairs you want to be used as the config. The Pydantic V1 behavior to create a class called `Config`
  in the namespace of the parent `BaseModel` subclass is now deprecated.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L202-L206",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:333",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:e1f3d2c94b7b820272f735d645e2275621fd5936896a347fc1f7879eb3674b53",
  "contributions": [
    {
      "content_end": 333,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L202-L206"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:883046956d69fc69fa76cd3a28d772a46f067d517f5d679bb3e3a6dfcc7b3383",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to config"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L202-L206",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 202,
      "last": 206,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-from-orm

Evidence ID: `evidence:da3e85d95eeb3b3bd713254506e0318c573ace5ae089e9651ea775a077f034bc`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
* The `from_orm` method has been deprecated; you can now just use `model_validate` (equivalent to `parse_obj` from
  Pydantic V1) to achieve something similar, as long as you've set `from_attributes=True` in the model config.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L99-L100",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:226",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:748c13e00741c70113887f049bafcfef7e6bfd26c0c2135692350c2b9d256fd2",
  "contributions": [
    {
      "content_end": 226,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L99-L100"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:da3e85d95eeb3b3bd713254506e0318c573ace5ae089e9651ea775a077f034bc",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to `pydantic.BaseModel`"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L99-L100",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 99,
      "last": 100,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-methods

Evidence ID: `evidence:b7182dc833aa33ab0c632c644e5bf752f05782964ec65a2ea7bc36fdd5780d97`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
### Changes to `pydantic.BaseModel`

Various method names have been changed; all non-deprecated `BaseModel` methods now have names matching either the
format `model_.*` or `__.*pydantic.*__`. Where possible, we have retained the deprecated methods with their old names
to help ease migration, but calling them will emit `DeprecationWarning`s.

| Pydantic V1 | Pydantic V2  |
| ----------- | ------------ |
| `__fields__` | `model_fields` |
| `__private_attributes__` | `__pydantic_private__` |
| `__validators__` | `__pydantic_validator__` |
| `construct()` | `model_construct()` |
| `copy()` | `model_copy()` |
| `dict()` | `model_dump()` |
| `json_schema()` | `model_json_schema()` |
| `json()` | `model_dump_json()` |
| `parse_obj()` | `model_validate()` |
| `update_forward_refs()` | `model_rebuild()` |

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L78-L95",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:808",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:d3a6af62baaabbefaa82b2f4b99dd923ddcde6490bcf61a6b142d5eb679df055",
  "contributions": [
    {
      "content_end": 808,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L78-L95"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:b7182dc833aa33ab0c632c644e5bf752f05782964ec65a2ea7bc36fdd5780d97",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to `pydantic.BaseModel`"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L78-L95",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 78,
      "last": 95,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-nullable

Evidence ID: `evidence:61acbc5d8912615c0a0e3598fe03c66a8fff0b5a61f7cfc6cf930276d3e51cc8`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
#### Required, optional, and nullable fields

Pydantic V2 changes some of the logic for specifying whether a field annotated as `Optional` is required
(i.e., has no default value) or not (i.e., has a default value of `None` or any other value of the corresponding type), and now more closely matches the
behavior of `dataclasses`. Similarly, fields annotated as `Any` no longer have a default value of `None`.

The following table describes the behavior of field annotations in V2:

| State                                                 | Field Definition            |
|-------------------------------------------------------|-----------------------------|
| Required, cannot be `None`                            | `f1: str`                   |
| Not required, cannot be `None`, is `'abc'` by default | `f2: str = 'abc'`           |
| Required, can be `None`                               | `f3: Optional[str]`         |
| Not required, can be `None`, is `None` by default     | `f4: Optional[str] = None`  |
| Not required, can be `None`, is `'abc'` by default    | `f5: Optional[str] = 'abc'` |
| Required, can be any type (including `None`)          | `f6: Any`                   |
| Not required, can be any type (including `None`)      | `f7: Any = None`            |


!!! note
    A field annotated as `typing.Optional[T]` will be required, and will allow for a value of `None`.
    It does not mean that the field has a default value of `None`. _(This is a breaking change from V1.)_

!!! note
    Any default value if provided makes a field not required.

Here is a code example demonstrating the above:
```py
from typing import Optional

from pydantic import BaseModel, ValidationError


class Foo(BaseModel):
    f1: str  # required, cannot be None
    f2: Optional[str]  # required, can be None - same as str | None
    f3: Optional[str] = None  # not required, can be None
    f4: str = 'Foobar'  # not required, but cannot be None


try:
    Foo(f1=None, f2=None, f4='b')
except ValidationError as e:
    print(e)
    """
    1 validation error for Foo
    f1
      Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    """
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L526-L575",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:2183",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:1dcdfc73c6b43bf5a4092069213bdd8629bcafc240a84182df678b48227cab01",
  "contributions": [
    {
      "content_end": 2183,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L526-L575"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:61acbc5d8912615c0a0e3598fe03c66a8fff0b5a61f7cfc6cf930276d3e51cc8",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to Handling of Standard Types",
    "Required, optional, and nullable fields"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L526-L575",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 526,
      "last": 575,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-orm-setting

Evidence ID: `evidence:60c76235152cb5d1ae54f8cd577c0779be723e81729971c54eae67cddf89c2c1`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
* The following config settings have been renamed:
    * `orm_mode` → `from_attributes`

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L230-L230",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:51:88",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:7bd47e0aa8294c01322754ce367d5cbb0d78f482506e07018d13ac6fa42b3aa0",
  "contributions": [
    {
      "content_end": 51,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L222-L222"
    },
    {
      "content_end": 88,
      "content_start": 51,
      "role": "supporting_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L230-L230"
    }
  ],
  "curator_notes": "Pending human review. Only the renamed-settings parent bullet and orm_mode entry are retained; other settings are excluded.",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:60c76235152cb5d1ae54f8cd577c0779be723e81729971c54eae67cddf89c2c1",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to config"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L222-L222",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 222,
      "last": 222,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    },
    {
      "first": 230,
      "last": 230,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-subclasses

Evidence ID: `evidence:b35a6a3ea3647392d775a0ffcc87965fb59371889f6636cc74403594c32f63e0`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
* We have changed the behavior related to serializing subclasses of models when they occur as nested fields in a parent
  model. In V1, we would always include all fields from the subclass instance. In V2, when we dump a model, we only
  include the fields that are defined on the annotated type of the field. This helps prevent some accidental security
  bugs. You can read more about this (including how to opt out of this behavior) in the
  [Subclass instances for fields of BaseModel, dataclasses, TypedDict](concepts/serialization.md#subclass-instances-for-fields-of-basemodel-dataclasses-typeddict)
  section of the model exporting docs.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L124-L129",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:644",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:d50521d41bc67b286669a3d7adf27932b56278ddec595841d5f8d85943a5a4c2",
  "contributions": [
    {
      "content_end": 644,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L124-L129"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:b35a6a3ea3647392d775a0ffcc87965fb59371889f6636cc74403594c32f63e0",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to `pydantic.BaseModel`"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L124-L129",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 124,
      "last": 129,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-typeerror

Evidence ID: `evidence:4bd23223de4ab66136b4944b2145e5c28ddbbc025f58c337cac6bf182c323bc5`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
#### `TypeError` is no longer converted to `ValidationError` in validators

Previously, when raising a `TypeError` within a validator function, that error would be wrapped into a `ValidationError`
and, in some cases (such as with FastAPI), these errors might be displayed to end users. This led to a variety of
undesirable behavior &mdash; for example, calling a function with the wrong signature might produce a user-facing
`ValidationError`.

However, in Pydantic V2, when a `TypeError` is raised in a validator, it is no longer converted into a
`ValidationError`:

```python
import pytest

from pydantic import BaseModel, field_validator  # or validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int) -> int:
        return str.lower(v)  # raises a TypeError


with pytest.raises(TypeError):
    Model(x=1)
```

This applies to all validation decorators.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L315-L343",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:902",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:093e07360cbfdafa34000027f03045c80998cf1ceeb4b0722e55e7eeb52a82e9",
  "contributions": [
    {
      "content_end": 902,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L315-L343"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:4bd23223de4ab66136b4944b2145e5c28ddbbc025f58c337cac6bf182c323bc5",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to validators",
    "`TypeError` is no longer converted to `ValidationError` in validators"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L315-L343",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 315,
      "last": 343,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## migration-validator

Evidence ID: `evidence:ea1ecf63c526ef552a3561a457e351903d098554729c0b4c6b3e786eefe66be3`

Original sources (document versions are not applicability labels):

- `source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a`: [docs/migration.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/migration.md); snapshot 2.5.3; sha256:b480fcf56406e3013152cf61cd8df68b57c6ba54f7d076f8c25fc55740477d2b

Full assembled content, quoted as data:

````text
#### `@validator` and `@root_validator` are deprecated

* `@validator` has been deprecated, and should be replaced with [`@field_validator`](concepts/validators.md), which provides various new features
    and improvements.
    * The new `@field_validator` decorator does not have the `each_item` keyword argument; validators you want to
        apply to items within a generic container should be added by annotating the type argument. See
        [validators in Annotated metadata](concepts/validators.md#generic-validated-collections) for details.
        This looks like `List[Annotated[int, Field(ge=0)]]`
    * Even if you keep using the deprecated `@validator` decorator, you can no longer add the `field` or
        `config` arguments to the signature of validator functions. If you need access to these, you'll need
        to migrate to `@field_validator` — see the [next section](#changes-to-validators-allowed-signatures)
        for more details.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L238-L249",
      "basis_source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "content_locator": "chars:0:960",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:61c4915f5fbc7e807c232fe3ea3dd614a15966b1a54d1112400314c7b457ab9d",
  "contributions": [
    {
      "content_end": 960,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "source_locator": "L238-L249"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:ea1ecf63c526ef552a3561a457e351903d098554729c0b4c6b3e786eefe66be3",
  "section_path": [
    "docs/migration.md",
    "Migration guide",
    "Changes to validators",
    "`@validator` and `@root_validator` are deprecated"
  ],
  "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
  "source_locator": "L238-L249",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 238,
      "last": 249,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5eb2ab457d9ecebcca1a0d169e019477ee2bc06a4f3c9159e7acae5ed5a1dd3a",
      "suffix": ""
    }
  ]
}
```

## v1-config

Evidence ID: `evidence:b6cb2402ea041bab4b014f341d2434c8ed8615cda00a26a1fa398719ffa13c80`

Original sources (document versions are not applicability labels):

- `source:cdcbaf4b67aef9a7e11e1030e58c4e024c6a0f2dc856df6321932cc29046ed47`: [docs/examples/model_config_main.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/model_config_main.py); snapshot 1.10.13; sha256:2d5f423feb2e2baf0e2c63df94ef2183b0b212984a167dd7ebbe67650132b9f2
- `source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e`: [docs/usage/model_config.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/model_config.md); snapshot 1.10.13; sha256:61536853429f1286b9d024e3f9fa3461cd88c78a217e58968e9d23fdaf3d191d

Full assembled content, quoted as data:

````text
Behaviour of _pydantic_ can be controlled via the `Config` class on a model or a _pydantic_ dataclass.

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    v: str

    class Config:
        max_anystr_length = 10
        error_msg_templates = {
            'value_error.any_str.max_length': 'max_length:{limit_value}',
        }


try:
    Model(v='x' * 20)
except ValidationError as e:
    print(e)
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L1-L1",
      "basis_source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "content_locator": "chars:0:103",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:d7d3d0d7b8d9bbf582921fc973baf61fdd032995aa708d806c8e1963d663129c",
  "contributions": [
    {
      "content_end": 104,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "source_locator": "L1-L2"
    },
    {
      "content_end": 440,
      "content_start": 104,
      "role": "companion_example",
      "source_id": "source:cdcbaf4b67aef9a7e11e1030e58c4e024c6a0f2dc856df6321932cc29046ed47",
      "source_locator": "L1-L17"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:b6cb2402ea041bab4b014f341d2434c8ed8615cda00a26a1fa398719ffa13c80",
  "section_path": [
    "docs/usage/model_config.md"
  ],
  "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
  "source_locator": "L1-L2",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:cdcbaf4b67aef9a7e11e1030e58c4e024c6a0f2dc856df6321932cc29046ed47",
      "first": 3,
      "last": 3,
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e"
    }
  ],
  "parts": [
    {
      "first": 1,
      "last": 2,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 17,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:cdcbaf4b67aef9a7e11e1030e58c4e024c6a0f2dc856df6321932cc29046ed47",
      "suffix": "```\n"
    }
  ]
}
```

## v1-dict

Evidence ID: `evidence:4f79eb319d7c82bd8ef1e1ba845de73e6d26eb90d328d962021b9b6346a3876c`

Original sources (document versions are not applicability labels):

- `source:8b9b8d6e289d40f980a6f71f7e3fbcc39dae3523a2d56701f0eeb946dc89ab95`: [docs/examples/exporting_models_dict.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/exporting_models_dict.py); snapshot 1.10.13; sha256:4683e7bc7218ffb7332a3970672f41cecc2da7829ee60f1f003646a824369511
- `source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c`: [docs/usage/exporting_models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/exporting_models.md); snapshot 1.10.13; sha256:a03261c6f99e155cbc6f302c6558478a6b21535c1f70c3d467ceffbf9ea05139

Full assembled content, quoted as data:

````text
## `model.dict(...)`

This is the primary way of converting a model to a dictionary. Sub-models will be recursively converted to dictionaries.

Arguments:

* `include`: fields to include in the returned dictionary; see [below](#advanced-include-and-exclude)
* `exclude`: fields to exclude from the returned dictionary; see [below](#advanced-include-and-exclude)
* `by_alias`: whether field aliases should be used as keys in the returned dictionary; default `False`
* `exclude_unset`: whether fields which were not explicitly set when creating the model should
  be excluded from the returned dictionary; default `False`.
  Prior to **v1.0**, `exclude_unset` was known as `skip_defaults`; use of `skip_defaults` is now deprecated
* `exclude_defaults`: whether fields which are equal to their default values (whether set or otherwise) should
  be excluded from the returned dictionary; default `False`
* `exclude_none`: whether fields which are equal to `None` should be excluded from the returned dictionary; default
  `False`

Example:

```python
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

# returns a dictionary:
print(m.dict())
print(m.dict(include={'foo', 'bar'}))
print(m.dict(exclude={'foo', 'bar'}))
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L6-L19",
      "basis_source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "content_locator": "chars:22:1026",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:b084005f202b1743af077c69da3490d911ebde4d6ae10bde216c9c1a3019b064",
  "contributions": [
    {
      "content_end": 1037,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "source_locator": "L4-L22"
    },
    {
      "content_end": 1394,
      "content_start": 1037,
      "role": "companion_example",
      "source_id": "source:8b9b8d6e289d40f980a6f71f7e3fbcc39dae3523a2d56701f0eeb946dc89ab95",
      "source_locator": "L1-L19"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:4f79eb319d7c82bd8ef1e1ba845de73e6d26eb90d328d962021b9b6346a3876c",
  "section_path": [
    "docs/usage/exporting_models.md",
    "`model.dict(...)`"
  ],
  "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
  "source_locator": "L4-L22",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:8b9b8d6e289d40f980a6f71f7e3fbcc39dae3523a2d56701f0eeb946dc89ab95",
      "first": 23,
      "last": 23,
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c"
    }
  ],
  "parts": [
    {
      "first": 4,
      "last": 22,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 19,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:8b9b8d6e289d40f980a6f71f7e3fbcc39dae3523a2d56701f0eeb946dc89ab95",
      "suffix": "```\n"
    }
  ]
}
```

## v1-errors

Evidence ID: `evidence:d7267def0efc3affe89aebfe80b279bd6910209fc2db679c5c98f16571254127`

Original sources (document versions are not applicability labels):

- `source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98`: [docs/usage/models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/models.md); snapshot 1.10.13; sha256:93a04c0e93631d0e7be8910014a3176b07502b4852e5ba606ffa693d7c2a6c21

Full assembled content, quoted as data:

````text
## Error Handling

*pydantic* will raise `ValidationError` whenever it finds an error in the data it's validating.

!!! note
    Validation code should not raise `ValidationError` itself, but rather raise `ValueError`, `TypeError` or
    `AssertionError` (or subclasses of `ValueError` or `TypeError`) which will be caught and used to populate
    `ValidationError`.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L174-L179",
      "basis_source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "content_locator": "chars:19:367",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:e01e378dfeae97961e0297f29a4d457fc2dbb1c12fb274681c7e3dfa2bb205e9",
  "contributions": [
    {
      "content_end": 367,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L172-L179"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:d7267def0efc3affe89aebfe80b279bd6910209fc2db679c5c98f16571254127",
  "section_path": [
    "docs/usage/models.md",
    "Error Handling"
  ],
  "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
  "source_locator": "L172-L179",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 172,
      "last": 179,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    }
  ]
}
```

## v1-extra

Evidence ID: `evidence:b84bfd24fd6881120fb7e04bfe9f7c5dc9b6eb258d64c94e4abc927cb51d4a27`

Original sources (document versions are not applicability labels):

- `source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e`: [docs/usage/model_config.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/model_config.md); snapshot 1.10.13; sha256:61536853429f1286b9d024e3f9fa3461cd88c78a217e58968e9d23fdaf3d191d

Full assembled content, quoted as data:

````text
**`extra`**
: whether to ignore, allow, or forbid extra attributes during model initialization. Accepts the string values of
  `'ignore'`, `'allow'`, or `'forbid'`, or values of the `Extra` enum (default: `Extra.ignore`).
  `'forbid'` will cause validation to fail if extra attributes are included, `'ignore'` will silently ignore any extra attributes,
  and `'allow'` will assign the attributes to the model.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L34-L38",
      "basis_source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "content_locator": "chars:0:410",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:1bf9eaf32434cdba08b0b7c96d0e0cf727cadfb785e1ed90b6582642ce9dc2ea",
  "contributions": [
    {
      "content_end": 410,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "source_locator": "L34-L38"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:b84bfd24fd6881120fb7e04bfe9f7c5dc9b6eb258d64c94e4abc927cb51d4a27",
  "section_path": [
    "docs/usage/model_config.md",
    "Options"
  ],
  "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
  "source_locator": "L34-L38",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 34,
      "last": 38,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "suffix": ""
    }
  ]
}
```

## v1-iteration

Evidence ID: `evidence:6a88147979a8479686c02647b54f0d0bdd5bb6b1033480da56d019f52353c7ae`

Original sources (document versions are not applicability labels):

- `source:b9335424ac067acc0027f439fabc55dea8fe4a07602e9566a961a933b8c491b4`: [docs/examples/exporting_models_iterate.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/exporting_models_iterate.py); snapshot 1.10.13; sha256:0ebbcba20e3f9666fb4515fe78ae46ebee1079ddf555cdb2235ecba6e5a109ea
- `source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c`: [docs/usage/exporting_models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/exporting_models.md); snapshot 1.10.13; sha256:a03261c6f99e155cbc6f302c6558478a6b21535c1f70c3d467ceffbf9ea05139

Full assembled content, quoted as data:

````text
## `dict(model)` and iteration

*pydantic* models can also be converted to dictionaries using `dict(model)`, and you can also
iterate over a model's field using `for field_name, value in model:`. With this approach the raw field values are
returned, so sub-models will not be converted to dictionaries.

Example:

```python
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

print(dict(m))
for name, value in m:
    print(f'{name}: {value}')
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L27-L29",
      "basis_source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "content_locator": "chars:32:303",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:d7ae2db3586f41bfe342ca0c32c4f840d4f58939dff10e55d6b7fd48eb7fb3d7",
  "contributions": [
    {
      "content_end": 314,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "source_locator": "L25-L32"
    },
    {
      "content_end": 622,
      "content_start": 314,
      "role": "companion_example",
      "source_id": "source:b9335424ac067acc0027f439fabc55dea8fe4a07602e9566a961a933b8c491b4",
      "source_locator": "L1-L18"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:6a88147979a8479686c02647b54f0d0bdd5bb6b1033480da56d019f52353c7ae",
  "section_path": [
    "docs/usage/exporting_models.md",
    "`dict(model)` and iteration"
  ],
  "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
  "source_locator": "L25-L32",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:b9335424ac067acc0027f439fabc55dea8fe4a07602e9566a961a933b8c491b4",
      "first": 33,
      "last": 33,
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c"
    }
  ],
  "parts": [
    {
      "first": 25,
      "last": 32,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 18,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:b9335424ac067acc0027f439fabc55dea8fe4a07602e9566a961a933b8c491b4",
      "suffix": "```\n"
    }
  ]
}
```

## v1-nested-filter

Evidence ID: `evidence:066375dd8bb4dd93910cb6c4aaa4fba632ca2a055579368f5aae15ac072f27da`

Original sources (document versions are not applicability labels):

- `source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c`: [docs/usage/exporting_models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/exporting_models.md); snapshot 1.10.13; sha256:a03261c6f99e155cbc6f302c6558478a6b21535c1f70c3d467ceffbf9ea05139
- `source:d4f8355782fb6357698ace44703691836ab577709fe135d58240b7658d0eff5c`: [docs/examples/exporting_models_exclude1.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/exporting_models_exclude1.py); snapshot 1.10.13; sha256:ef48913ab2389bfe361a4e54d2574ee250d8ed012cfd96ad9ccff461fef4dcf7

Full assembled content, quoted as data:

````text
## Advanced include and exclude

The `dict`, `json`, and `copy` methods support `include` and `exclude` arguments which can either be
sets or dictionaries. This allows nested selection of which fields to export:

```python
from pydantic import BaseModel, SecretStr


class User(BaseModel):
    id: int
    username: str
    password: SecretStr


class Transaction(BaseModel):
    id: str
    user: User
    value: int


t = Transaction(
    id='1234567890',
    user=User(
        id=42,
        username='JohnDoe',
        password='hashedpassword'
    ),
    value=9876543210,
)

# using a set:
print(t.dict(exclude={'user', 'value'}))

# using a dict:
print(t.dict(exclude={'user': {'username', 'password'}, 'value': True}))

print(t.dict(include={'id': True, 'user': {'id'}}))
```

The `True` indicates that we want to exclude or include an entire key, just as if we included it in a set.
Of course, the same can be done at any depth level.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L135-L136",
      "basis_source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "content_locator": "chars:33:212",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:844d8b52d1bf2d38170e25c015df7e2cbfc1e5f2ddae217b84f72bdfb702da25",
  "contributions": [
    {
      "content_end": 213,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "source_locator": "L133-L137"
    },
    {
      "content_end": 785,
      "content_start": 213,
      "role": "companion_example",
      "source_id": "source:d4f8355782fb6357698ace44703691836ab577709fe135d58240b7658d0eff5c",
      "source_locator": "L1-L32"
    },
    {
      "content_end": 945,
      "content_start": 785,
      "role": "supporting_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "source_locator": "L139-L141"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:066375dd8bb4dd93910cb6c4aaa4fba632ca2a055579368f5aae15ac072f27da",
  "section_path": [
    "docs/usage/exporting_models.md",
    "Advanced include and exclude"
  ],
  "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
  "source_locator": "L133-L137",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:d4f8355782fb6357698ace44703691836ab577709fe135d58240b7658d0eff5c",
      "first": 138,
      "last": 138,
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c"
    }
  ],
  "parts": [
    {
      "first": 133,
      "last": 137,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 32,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:d4f8355782fb6357698ace44703691836ab577709fe135d58240b7658d0eff5c",
      "suffix": "```\n"
    },
    {
      "first": 139,
      "last": 141,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "suffix": ""
    }
  ]
}
```

## v1-nullable

Evidence ID: `evidence:dbe99fbadce62a074aa9f9cfd04fefb4f64e6b3c6ceb094a6dc7a5bb5eb6cced`

Original sources (document versions are not applicability labels):

- `source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98`: [docs/usage/models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/models.md); snapshot 1.10.13; sha256:93a04c0e93631d0e7be8910014a3176b07502b4852e5ba606ffa693d7c2a6c21
- `source:7cc2e598ca6e3adf75a17e29ad5006c795c9909e1ed7361cae49020446168429`: [docs/examples/models_required_field_optional.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/models_required_field_optional.py); snapshot 1.10.13; sha256:88691fc4f56f93aa118fb3b789685cc801af5b5d93bac3e3d68ed91209d8510d

Full assembled content, quoted as data:

````text
### Required Optional fields

!!! warning
    Since version **v1.2** annotation only nullable (`Optional[...]`, `Union[None, ...]` and `Any`) fields and nullable
    fields with an ellipsis (`...`) as the default value, no longer mean the same thing.

    In some situations this may cause **v1.2** to not be entirely backwards compatible with earlier **v1.*** releases.

If you want to specify a field that can take a `None` value while still being required,
you can use `Optional` with `...`:

```python
from typing import Optional
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    a: Optional[int]
    b: Optional[int] = ...
    c: Optional[int] = Field(...)


print(Model(b=1, c=2))
try:
    Model(a=1, b=2)
except ValidationError as e:
    print(e)
```

In this model, `a`, `b`, and `c` can take `None` as a value. But `a` is optional, while `b` and `c` are required.
`b` and `c` require a value, even if the value is `None`.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L451-L452",
      "basis_source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "content_locator": "chars:372:495",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:4622d6a967cb999c11230615b6585cc7b3301fe946e219fee47737cca32b6230",
  "contributions": [
    {
      "content_end": 496,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L443-L453"
    },
    {
      "content_end": 793,
      "content_start": 496,
      "role": "companion_example",
      "source_id": "source:7cc2e598ca6e3adf75a17e29ad5006c795c9909e1ed7361cae49020446168429",
      "source_locator": "L1-L15"
    },
    {
      "content_end": 966,
      "content_start": 793,
      "role": "supporting_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L455-L457"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:dbe99fbadce62a074aa9f9cfd04fefb4f64e6b3c6ceb094a6dc7a5bb5eb6cced",
  "section_path": [
    "docs/usage/models.md",
    "Required fields",
    "Required Optional fields"
  ],
  "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
  "source_locator": "L443-L453",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:7cc2e598ca6e3adf75a17e29ad5006c795c9909e1ed7361cae49020446168429",
      "first": 454,
      "last": 454,
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98"
    }
  ],
  "parts": [
    {
      "first": 443,
      "last": 453,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 15,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:7cc2e598ca6e3adf75a17e29ad5006c795c9909e1ed7361cae49020446168429",
      "suffix": "```\n"
    },
    {
      "first": 455,
      "last": 457,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    }
  ]
}
```

## v1-orm

Evidence ID: `evidence:812c551c52b07ddf921401d978ad281a6d4604f27ddc2f0215961bed9e107fec`

Original sources (document versions are not applicability labels):

- `source:42a7f99d419ff673c85f2bd317253ca1fd15ab38066f1bccc537b2b7b8b4bf72`: [docs/examples/models_orm_mode.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/models_orm_mode.py); snapshot 1.10.13; sha256:d6b7c74f36e6e508d895145e5af0062e5f0354764d40646f8d194596855e4a2b
- `source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98`: [docs/usage/models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/models.md); snapshot 1.10.13; sha256:93a04c0e93631d0e7be8910014a3176b07502b4852e5ba606ffa693d7c2a6c21

Full assembled content, quoted as data:

````text
## ORM Mode (aka Arbitrary Class Instances)

Pydantic models can be created from arbitrary class instances to support models that map to ORM objects.

To do this:

1. The [Config](model_config.md) property `orm_mode` must be set to `True`.
2. The special constructor `from_orm` must be used to create the model instance.

The example here uses SQLAlchemy, but the same approach should work for any ORM.

```python
from typing import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, constr

Base = declarative_base()


class CompanyOrm(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, nullable=False)
    public_key = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(63), unique=True)
    domains = Column(ARRAY(String(255)))


class CompanyModel(BaseModel):
    id: int
    public_key: constr(max_length=20)
    name: constr(max_length=63)
    domains: List[constr(max_length=255)]

    class Config:
        orm_mode = True


co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    name='Testing',
    domains=['example.com', 'foobar.com'],
)
print(co_orm)
co_model = CompanyModel.from_orm(co_orm)
print(co_model)
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L124-L131",
      "basis_source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "content_locator": "chars:45:403",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:afc06da0f3deda70f874999df45a69d95d57430e674edfa6bf3f69193954d86f",
  "contributions": [
    {
      "content_end": 404,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L122-L132"
    },
    {
      "content_end": 1334,
      "content_start": 404,
      "role": "companion_example",
      "source_id": "source:42a7f99d419ff673c85f2bd317253ca1fd15ab38066f1bccc537b2b7b8b4bf72",
      "source_locator": "L1-L36"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:812c551c52b07ddf921401d978ad281a6d4604f27ddc2f0215961bed9e107fec",
  "section_path": [
    "docs/usage/models.md",
    "ORM Mode (aka Arbitrary Class Instances)"
  ],
  "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
  "source_locator": "L122-L132",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:42a7f99d419ff673c85f2bd317253ca1fd15ab38066f1bccc537b2b7b8b4bf72",
      "first": 133,
      "last": 133,
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98"
    }
  ],
  "parts": [
    {
      "first": 122,
      "last": 132,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 36,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:42a7f99d419ff673c85f2bd317253ca1fd15ab38066f1bccc537b2b7b8b4bf72",
      "suffix": "```\n"
    }
  ]
}
```

## v1-orm-option

Evidence ID: `evidence:dabe9d5ec1597dbefad71ecda95e40df288cb31a0cca8ccb300ee1f10f245da3`

Original sources (document versions are not applicability labels):

- `source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e`: [docs/usage/model_config.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/model_config.md); snapshot 1.10.13; sha256:61536853429f1286b9d024e3f9fa3461cd88c78a217e58968e9d23fdaf3d191d

Full assembled content, quoted as data:

````text
**`orm_mode`**
: whether to allow usage of [ORM mode](models.md#orm-mode-aka-arbitrary-class-instances)

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L85-L86",
      "basis_source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "content_locator": "chars:0:104",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:4042167e64da0aed3a6b63f4afb6d17c79cae3d15a9015fe3859310369f3036e",
  "contributions": [
    {
      "content_end": 104,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "source_locator": "L85-L86"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:dabe9d5ec1597dbefad71ecda95e40df288cb31a0cca8ccb300ee1f10f245da3",
  "section_path": [
    "docs/usage/model_config.md",
    "Options"
  ],
  "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
  "source_locator": "L85-L86",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 85,
      "last": 86,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:e3ef0609f76c2aa3569eab65f599c520c7ed78b9f373bc3a63e22e0a9916a45e",
      "suffix": ""
    }
  ]
}
```

## v1-parse-obj

Evidence ID: `evidence:80a4ff35755ad525346d42bc58e669c02c3c045fff9b6930b838e42b182895bb`

Original sources (document versions are not applicability labels):

- `source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98`: [docs/usage/models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/models.md); snapshot 1.10.13; sha256:93a04c0e93631d0e7be8910014a3176b07502b4852e5ba606ffa693d7c2a6c21
- `source:bface2a509d560bcca49984aa3863bad490c5673ee18dc28532a0b1919d10d34`: [docs/examples/models_parse.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/models_parse.py); snapshot 1.10.13; sha256:4f1c98d462e5cc18b5e09ff97ac57ffc030018d47f650f01d91d56348667fa97

Full assembled content, quoted as data:

````text
## Helper Functions

* **`parse_obj`**: this is very similar to the `__init__` method of the model, except it takes a dict
  rather than keyword arguments. If the object passed is not a dict a `ValidationError` will be raised.

```python
from datetime import datetime

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name = 'John Doe'
    signup_ts: datetime = None


m = User.parse_obj({'id': 123, 'name': 'James'})
print(m)

try:
    User.parse_obj(['not', 'a', 'dict'])
except ValidationError as e:
    print(e)
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L231-L232",
      "basis_source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "content_locator": "chars:21:227",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:916299227e591c5b4a472de4650265b8094d6a22a893df9ddd37efb74e911272",
  "contributions": [
    {
      "content_end": 21,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L227-L228"
    },
    {
      "content_end": 227,
      "content_start": 21,
      "role": "supporting_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L231-L232"
    },
    {
      "content_end": 269,
      "content_start": 227,
      "role": "companion_example",
      "source_id": "source:bface2a509d560bcca49984aa3863bad490c5673ee18dc28532a0b1919d10d34",
      "source_locator": "L2-L2"
    },
    {
      "content_end": 560,
      "content_start": 269,
      "role": "companion_example",
      "source_id": "source:bface2a509d560bcca49984aa3863bad490c5673ee18dc28532a0b1919d10d34",
      "source_locator": "L5-L20"
    }
  ],
  "curator_notes": "Pending human review. Omitted helper-count introduction and unrelated parse_raw/parse_file text; only relevant imports and parse_obj code retained.",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:80a4ff35755ad525346d42bc58e669c02c3c045fff9b6930b838e42b182895bb",
  "section_path": [
    "docs/usage/models.md",
    "Helper Functions"
  ],
  "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
  "source_locator": "L227-L228",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:bface2a509d560bcca49984aa3863bad490c5673ee18dc28532a0b1919d10d34",
      "first": 238,
      "last": 238,
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98"
    }
  ],
  "parts": [
    {
      "first": 227,
      "last": 228,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    },
    {
      "first": 231,
      "last": 232,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    },
    {
      "first": 2,
      "last": 2,
      "prefix": "\n```python\n",
      "role": "companion_example",
      "source_id": "source:bface2a509d560bcca49984aa3863bad490c5673ee18dc28532a0b1919d10d34",
      "suffix": "\n"
    },
    {
      "first": 5,
      "last": 20,
      "prefix": "",
      "role": "companion_example",
      "source_id": "source:bface2a509d560bcca49984aa3863bad490c5673ee18dc28532a0b1919d10d34",
      "suffix": "```\n"
    }
  ]
}
```

## v1-pre-item

Evidence ID: `evidence:e621fdbd4927656e460324576059d928af9ebbfd21ed0a445ecf0fa47cb5aab3`

Original sources (document versions are not applicability labels):

- `source:ce5afe23ec92adab45b63afbd17b3db48433e07aa48b00301375b143d8cc66dd`: [docs/examples/validators_pre_item.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/validators_pre_item.py); snapshot 1.10.13; sha256:627d4b911804d6f141679f528199c3e0c70cadfe88613a0b402117e47a797504
- `source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad`: [docs/usage/validators.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/validators.md); snapshot 1.10.13; sha256:d310eb09d07df7eb75382fca955e2fdc38af5d7f89ce329afe818177cab4088d

Full assembled content, quoted as data:

````text
## Pre and per-item validators

Validators can do a few more complex things:

```python
from typing import List
from pydantic import BaseModel, ValidationError, validator


class DemoModel(BaseModel):
    square_numbers: List[int] = []
    cube_numbers: List[int] = []

    # '*' is the same as 'cube_numbers', 'square_numbers' here:
    @validator('*', pre=True)
    def split_str(cls, v):
        if isinstance(v, str):
            return v.split('|')
        return v

    @validator('cube_numbers', 'square_numbers')
    def check_sum(cls, v):
        if sum(v) > 42:
            raise ValueError('sum of numbers greater than 42')
        return v

    @validator('square_numbers', each_item=True)
    def check_squares(cls, v):
        assert v ** 0.5 % 1 == 0, f'{v} is not a square number'
        return v

    @validator('cube_numbers', each_item=True)
    def check_cubes(cls, v):
        # 64 ** (1 / 3) == 3.9999999999999996 (!)
        # this is not a good way of checking cubes
        assert v ** (1 / 3) % 1 == 0, f'{v} is not a cubed number'
        return v


print(DemoModel(square_numbers=[1, 4, 9]))
print(DemoModel(square_numbers='1|4|16'))
print(DemoModel(square_numbers=[16], cube_numbers=[8, 27]))
try:
    DemoModel(square_numbers=[1, 4, 2])
except ValidationError as e:
    print(e)

try:
    DemoModel(cube_numbers=[27, 27])
except ValidationError as e:
    print(e)
```

A few more things to note:

* a single validator can be applied to multiple fields by passing it multiple field names
* a single validator can also be called on *all* fields by passing the special value `'*'`
* the keyword argument `pre` will cause the validator to be called prior to other validation
* passing `each_item=True` will result in the validator being applied to individual values
  (e.g. of `List`, `Dict`, `Set`, etc.), rather than the whole object

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L43-L45",
      "basis_source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "content_locator": "chars:1609:1863",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:3f3f43f154fad65c0fef377b78447a8e65865f57fedbf1b3dd105385fc9a8437",
  "contributions": [
    {
      "content_end": 78,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "source_locator": "L33-L36"
    },
    {
      "content_end": 1399,
      "content_start": 78,
      "role": "companion_example",
      "source_id": "source:ce5afe23ec92adab45b63afbd17b3db48433e07aa48b00301375b143d8cc66dd",
      "source_locator": "L1-L46"
    },
    {
      "content_end": 1863,
      "content_start": 1399,
      "role": "supporting_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "source_locator": "L38-L45"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:e621fdbd4927656e460324576059d928af9ebbfd21ed0a445ecf0fa47cb5aab3",
  "section_path": [
    "docs/usage/validators.md",
    "Pre and per-item validators"
  ],
  "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
  "source_locator": "L33-L36",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:ce5afe23ec92adab45b63afbd17b3db48433e07aa48b00301375b143d8cc66dd",
      "first": 37,
      "last": 37,
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad"
    }
  ],
  "parts": [
    {
      "first": 33,
      "last": 36,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 46,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:ce5afe23ec92adab45b63afbd17b3db48433e07aa48b00301375b143d8cc66dd",
      "suffix": "```\n"
    },
    {
      "first": 38,
      "last": 45,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "suffix": ""
    }
  ]
}
```

## v1-required

Evidence ID: `evidence:886499a7f09a03b7574da0a604b79dd83457ff6bbd5625d7bb934176175698be`

Original sources (document versions are not applicability labels):

- `source:23bb35430dac787c94d4aa8ebc0a1072429d7e4efd4f06b7df0a3cb0e0bbe058`: [docs/examples/models_required_fields.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/models_required_fields.py); snapshot 1.10.13; sha256:d93b7dd933edc8092dd0aab1f4e55c15e47545b5d88d75c7dfebd91b642f982d
- `source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98`: [docs/usage/models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/models.md); snapshot 1.10.13; sha256:93a04c0e93631d0e7be8910014a3176b07502b4852e5ba606ffa693d7c2a6c21

Full assembled content, quoted as data:

````text
## Required fields

To declare a field as required, you may declare it using just an annotation, or you may use an ellipsis (`...`) 
as the value:

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    a: int
    b: int = ...
    c: int = Field(...)
```

Where `Field` refers to the [field function](schema.md#field-customization).

Here `a`, `b` and `c` are all required. However, use of the ellipses in `b` will not work well
with [mypy](mypy.md), and as of **v1.0** should be avoided in most cases.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: the documented statement that the demonstrated int fields a, b, and c are required is proposed for 1.10.13 only, preserving its mypy caveat. Interpret docs/usage/models.md L440-L441 with the existing companion docs/examples/models_required_fields.py L4-L7. This does not assert unconditional requiredness for annotation-only Optional, Any, or every field declaration. Documentation is evidence, not runtime verification; human review remains pending.",
      "basis_locator": "L440-L441",
      "basis_source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "content_locator": "chars:357:526",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:9155342c33c17690ae483261f7cb1b6f0a0fa3c31c7972b15c39da803b3741e6",
  "contributions": [
    {
      "content_end": 148,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L431-L435"
    },
    {
      "content_end": 278,
      "content_start": 148,
      "role": "companion_example",
      "source_id": "source:23bb35430dac787c94d4aa8ebc0a1072429d7e4efd4f06b7df0a3cb0e0bbe058",
      "source_locator": "L1-L7"
    },
    {
      "content_end": 526,
      "content_start": 278,
      "role": "supporting_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "source_locator": "L437-L441"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:886499a7f09a03b7574da0a604b79dd83457ff6bbd5625d7bb934176175698be",
  "section_path": [
    "docs/usage/models.md",
    "Required fields"
  ],
  "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
  "source_locator": "L431-L435",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:23bb35430dac787c94d4aa8ebc0a1072429d7e4efd4f06b7df0a3cb0e0bbe058",
      "first": 436,
      "last": 436,
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98"
    }
  ],
  "parts": [
    {
      "first": 431,
      "last": 435,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 7,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:23bb35430dac787c94d4aa8ebc0a1072429d7e4efd4f06b7df0a3cb0e0bbe058",
      "suffix": "```\n"
    },
    {
      "first": 437,
      "last": 441,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:46173620f65358541d4ef5041bb4b10973373ddf7c1c50301a82d8c07e1a0f98",
      "suffix": ""
    }
  ]
}
```

## v1-sequence-filter

Evidence ID: `evidence:481e2f537c4f907d0b6d4f5c2c693d96e3d4569ed296d5b84a3067683769be4e`

Original sources (document versions are not applicability labels):

- `source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c`: [docs/usage/exporting_models.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/exporting_models.md); snapshot 1.10.13; sha256:a03261c6f99e155cbc6f302c6558478a6b21535c1f70c3d467ceffbf9ea05139
- `source:d86c4e4fa1cddbf1b37bc4a16b701e16027257cd2f3fe625a1f0c47c2f6cce0f`: [docs/examples/exporting_models_exclude2.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/exporting_models_exclude2.py); snapshot 1.10.13; sha256:7008346032ebc5d0d45c11575f025603f49d7f5bf6f6957115f5a72637bb1395

Full assembled content, quoted as data:

````text
Special care must be taken when including or excluding fields from a list or tuple of submodels or dictionaries.  In this scenario,
`dict` and related methods expect integer keys for element-wise inclusion or exclusion. To exclude a field from **every**
member of a list or tuple, the dictionary key `'__all__'` can be used as follows:

```python
import datetime
from typing import List

from pydantic import BaseModel, SecretStr


class Country(BaseModel):
    name: str
    phone_code: int


class Address(BaseModel):
    post_code: int
    country: Country


class CardDetails(BaseModel):
    number: SecretStr
    expires: datetime.date


class Hobby(BaseModel):
    name: str
    info: str


class User(BaseModel):
    first_name: str
    second_name: str
    address: Address
    card_details: CardDetails
    hobbies: List[Hobby]


user = User(
    first_name='John',
    second_name='Doe',
    address=Address(
        post_code=123456,
        country=Country(
            name='USA',
            phone_code=1
        )
    ),
    card_details=CardDetails(
        number=4212934504460000,
        expires=datetime.date(2020, 5, 1)
    ),
    hobbies=[
        Hobby(name='Programming', info='Writing code and stuff'),
        Hobby(name='Gaming', info='Hell Yeah!!!'),
    ],
)

exclude_keys = {
    'second_name': True,
    'address': {'post_code': True, 'country': {'phone_code'}},
    'card_details': True,
    # You can exclude fields from specific members of a tuple/list by index:
    'hobbies': {-1: {'info'}},
}

include_keys = {
    'first_name': True,
    'address': {'country': {'name'}},
    'hobbies': {0: True, -1: {'name'}},
}

# would be the same as user.dict(exclude=exclude_keys) in this case:
print(user.dict(include=include_keys))

# To exclude a field from all members of a nested list or tuple, use "__all__":
print(user.dict(exclude={'hobbies': {'__all__': {'info'}}}))
```

The same holds for the `json` and `copy` methods.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L143-L145",
      "basis_source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "content_locator": "chars:0:336",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:4fcc3f02cc915624b81e9da76773470ba71036fee8de68c638ddfc01f1db3680",
  "contributions": [
    {
      "content_end": 337,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "source_locator": "L143-L146"
    },
    {
      "content_end": 1907,
      "content_start": 337,
      "role": "companion_example",
      "source_id": "source:d86c4e4fa1cddbf1b37bc4a16b701e16027257cd2f3fe625a1f0c47c2f6cce0f",
      "source_locator": "L1-L73"
    },
    {
      "content_end": 1958,
      "content_start": 1907,
      "role": "supporting_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "source_locator": "L148-L149"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:481e2f537c4f907d0b6d4f5c2c693d96e3d4569ed296d5b84a3067683769be4e",
  "section_path": [
    "docs/usage/exporting_models.md",
    "Advanced include and exclude"
  ],
  "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
  "source_locator": "L143-L146",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:d86c4e4fa1cddbf1b37bc4a16b701e16027257cd2f3fe625a1f0c47c2f6cce0f",
      "first": 147,
      "last": 147,
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c"
    }
  ],
  "parts": [
    {
      "first": 143,
      "last": 146,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 73,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:d86c4e4fa1cddbf1b37bc4a16b701e16027257cd2f3fe625a1f0c47c2f6cce0f",
      "suffix": "```\n"
    },
    {
      "first": 148,
      "last": 149,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:d4cedfb24a1d1ff67c772d182fde9f6ec76dd3900a466b3f17cdade3617f669c",
      "suffix": ""
    }
  ]
}
```

## v1-validators

Evidence ID: `evidence:de3bf67621ae0433616b3b88bbad1052768664fea091db62c16a5f92c19fd83b`

Original sources (document versions are not applicability labels):

- `source:1b5a90b71c4385b0f2245630f20cc2976310d2863abaa08f080472a678514894`: [docs/examples/validators_simple.py](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/examples/validators_simple.py); snapshot 1.10.13; sha256:f04032a3791a01aff1ec8db580486a90e591dfcf96d7c3baeee8801be8b6b80b
- `source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad`: [docs/usage/validators.md](https://github.com/pydantic/pydantic/blob/8822578619bf8d0bb754b1cf7a2a905b50240d01/docs/usage/validators.md); snapshot 1.10.13; sha256:d310eb09d07df7eb75382fca955e2fdc38af5d7f89ce329afe818177cab4088d

Full assembled content, quoted as data:

````text
Custom validation and complex relationships between objects can be achieved using the `validator` decorator.

```python
from pydantic import BaseModel, ValidationError, validator


class UserModel(BaseModel):
    name: str
    username: str
    password1: str
    password2: str

    @validator('name')
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v


user = UserModel(
    name='samuel colvin',
    username='scolvin',
    password1='zxcvbn',
    password2='zxcvbn',
)
print(user)

try:
    UserModel(
        name='samuel',
        username='scolvin',
        password1='zxcvbn',
        password2='zxcvbn2',
    )
except ValidationError as e:
    print(e)
```

A few things to note on validators:

* validators are "class methods", so the first argument value they receive is the `UserModel` class, not an instance
  of `UserModel`.
* the second argument is always the field value to validate; it can be named as you please
* you can also add any subset of the following arguments to the signature (the names **must** match):
  * `values`: a dict containing the name-to-value mapping of any previously-validated fields
  * `config`: the model config
  * `field`: the field being validated. Type of object is `pydantic.fields.ModelField`.
  * `**kwargs`: if provided, this will include the arguments above not explicitly listed in the signature
* validators should either return the parsed value or raise a `ValueError`, `TypeError`, or `AssertionError`
  (``assert`` statements may be used).

!!! warning
    If you make use of `assert` statements, keep in mind that running
    Python with the [`-O` optimization flag](https://docs.python.org/3/using/cmdline.html#cmdoption-o)
    disables `assert` statements, and **validators will stop working**.

* where validators rely on other values, you should be aware that:

  * Validation is done in the order fields are defined.
    E.g. in the example above, `password2` has access to `password1` (and `name`),
    but `password1` does not have access to `password2`. See [Field Ordering](models.md#field-ordering)
    for more information on how fields are ordered

  * If validation fails on another field (or that field is missing) it will not be included in `values`, hence
    `if 'password1' in values and ...` in this example.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 1.10.13 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L1-L1",
      "basis_source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "content_locator": "chars:0:109",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:e03505f9a632f2dc6d90b4d01d83f8302d764c3bf84ec9aec197076a0a3d6ffe",
  "contributions": [
    {
      "content_end": 110,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "source_locator": "L1-L2"
    },
    {
      "content_end": 1110,
      "content_start": 110,
      "role": "companion_example",
      "source_id": "source:1b5a90b71c4385b0f2245630f20cc2976310d2863abaa08f080472a678514894",
      "source_locator": "L1-L44"
    },
    {
      "content_end": 2731,
      "content_start": 1110,
      "role": "supporting_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "source_locator": "L4-L31"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:de3bf67621ae0433616b3b88bbad1052768664fea091db62c16a5f92c19fd83b",
  "section_path": [
    "docs/usage/validators.md"
  ],
  "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
  "source_locator": "L1-L2",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [
    {
      "companion_source_id": "source:1b5a90b71c4385b0f2245630f20cc2976310d2863abaa08f080472a678514894",
      "first": 3,
      "last": 3,
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad"
    }
  ],
  "parts": [
    {
      "first": 1,
      "last": 2,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "suffix": ""
    },
    {
      "first": 1,
      "last": 44,
      "prefix": "```python\n",
      "role": "companion_example",
      "source_id": "source:1b5a90b71c4385b0f2245630f20cc2976310d2863abaa08f080472a678514894",
      "suffix": "```\n"
    },
    {
      "first": 4,
      "last": 31,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:f0bc9c56bef004636f0b9ea6ab1f9ac8d45e25726093f01a3f5f449bd7995aad",
      "suffix": ""
    }
  ]
}
```

## v2-attributes

Evidence ID: `evidence:e7d14e6e4abdf8b91c69ecbfe2d73153531359feb2017b8dc967a8fc5f3d01ab`

Original sources (document versions are not applicability labels):

- `source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d`: [docs/concepts/models.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/models.md); snapshot 2.5.3; sha256:ef0fb3734042b6b36d7da69fb3f4801af6eae4285b447854ff4a287993c8f42c

Full assembled content, quoted as data:

````text
## Arbitrary class instances

(Formerly known as "ORM Mode"/`from_orm`.)

Pydantic models can also be created from arbitrary class instances by reading the instance attributes corresponding
to the model field names. One common application of this functionality is integration with object-relational mappings
(ORMs).

To do this, set the config attribute `model_config['from_attributes'] = True`. See
[Model Config][pydantic.config.ConfigDict.from_attributes] and [ConfigDict][pydantic.config.ConfigDict] for more information.

The example here uses [SQLAlchemy](https://www.sqlalchemy.org/), but the same approach should work for any ORM.

```py
from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
from typing_extensions import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Base = declarative_base()


class CompanyOrm(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, nullable=False)
    public_key = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(63), unique=True)
    domains = Column(ARRAY(String(255)))


class CompanyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_key: Annotated[str, StringConstraints(max_length=20)]
    name: Annotated[str, StringConstraints(max_length=63)]
    domains: List[Annotated[str, StringConstraints(max_length=255)]]


co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    name='Testing',
    domains=['example.com', 'foobar.com'],
)
print(co_orm)
#> <__main__.CompanyOrm object at 0x0123456789ab>
co_model = CompanyModel.model_validate(co_orm)
print(co_model)
"""
id=123 public_key='foobar' name='Testing' domains=['example.com', 'foobar.com']
"""
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L237-L242",
      "basis_source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "content_locator": "chars:74:526",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:4b1b65c9c2dad647d2cbf2bef824a137a21591988caaa5ecf972c3fd42f5bc2a",
  "contributions": [
    {
      "content_end": 1855,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "source_locator": "L233-L290"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:e7d14e6e4abdf8b91c69ecbfe2d73153531359feb2017b8dc967a8fc5f3d01ab",
  "section_path": [
    "docs/concepts/models.md",
    "Arbitrary class instances"
  ],
  "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
  "source_locator": "L233-L290",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 233,
      "last": 290,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "suffix": ""
    }
  ]
}
```

## v2-config

Evidence ID: `evidence:6602b94e99222b815990638bbc8d9db96a5fc0bea5e270819c6c8b6ae326221b`

Original sources (document versions are not applicability labels):

- `source:3177ac9c7416d2cb5eff4207e35a6740c9f2feb34908de1e60817435b30bd10a`: [docs/concepts/config.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/config.md); snapshot 2.5.3; sha256:32f8bb5dbf52003c25fed28ed0d483f2d2d5d1fc7addfebd402c5c96677b8947

Full assembled content, quoted as data:

````text
Behaviour of Pydantic can be controlled via the [`BaseModel.model_config`][pydantic.BaseModel.model_config],
and as an argument to [`TypeAdapter`][pydantic.TypeAdapter].

!!! note
    Before **v2.0**, the `Config` class was used. This is still supported, but **deprecated**.

```py
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    model_config = ConfigDict(str_max_length=10)

    v: str


try:
    m = Model(v='x' * 20)
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    v
      String should have at most 10 characters [type=string_too_long, input_value='xxxxxxxxxxxxxxxxxxxx', input_type=str]
    """
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L1-L2",
      "basis_source_id": "source:3177ac9c7416d2cb5eff4207e35a6740c9f2feb34908de1e60817435b30bd10a",
      "content_locator": "chars:0:170",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    },
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L4-L5",
      "basis_source_id": "source:3177ac9c7416d2cb5eff4207e35a6740c9f2feb34908de1e60817435b30bd10a",
      "content_locator": "chars:171:275",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:a5f2932e1c351e822c9e217a24b3b1cc4c0a9943e043f1a393a9f7c678654aa0",
  "contributions": [
    {
      "content_end": 685,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:3177ac9c7416d2cb5eff4207e35a6740c9f2feb34908de1e60817435b30bd10a",
      "source_locator": "L1-L26"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:6602b94e99222b815990638bbc8d9db96a5fc0bea5e270819c6c8b6ae326221b",
  "section_path": [
    "docs/concepts/config.md"
  ],
  "source_id": "source:3177ac9c7416d2cb5eff4207e35a6740c9f2feb34908de1e60817435b30bd10a",
  "source_locator": "L1-L26",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 1,
      "last": 26,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:3177ac9c7416d2cb5eff4207e35a6740c9f2feb34908de1e60817435b30bd10a",
      "suffix": ""
    }
  ]
}
```

## v2-dump

Evidence ID: `evidence:ff1f3e3ee236ff1387cd370b65854454999d9ee70de571433c98a6e65aed1f1d`

Original sources (document versions are not applicability labels):

- `source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955`: [docs/concepts/serialization.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/serialization.md); snapshot 2.5.3; sha256:81c9d6d63677846feebdd0c5bc9770fa3a37078007468044b188dc988756da7e

Full assembled content, quoted as data:

````text
## `model.model_dump(...)`

??? api "API Documentation"
    [`pydantic.main.BaseModel.model_dump`][pydantic.main.BaseModel.model_dump]<br>

This is the primary way of converting a model to a dictionary. Sub-models will be recursively converted to dictionaries.

!!! note
    The one exception to sub-models being converted to dictionaries is that [`RootModel`](models.md#rootmodel-and-custom-root-types)
    and its subclasses will have the `root` field value dumped directly, without a wrapping dictionary. This is also
    done recursively.


!!! note
    You can use [computed fields](../api/fields.md#pydantic.fields.computed_field) to include `property` and
    `cached_property` data in the `model.model_dump(...)` output.

Example:

```py
from typing import Any, List, Optional

from pydantic import BaseModel, Field, Json


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: Optional[float] = 1.1
    foo: str = Field(serialization_alias='foo_alias')
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

# returns a dictionary:
print(m.model_dump())
#> {'banana': 3.14, 'foo': 'hello', 'bar': {'whatever': 123}}
print(m.model_dump(include={'foo', 'bar'}))
#> {'foo': 'hello', 'bar': {'whatever': 123}}
print(m.model_dump(exclude={'foo', 'bar'}))
#> {'banana': 3.14}
print(m.model_dump(by_alias=True))
#> {'banana': 3.14, 'foo_alias': 'hello', 'bar': {'whatever': 123}}
print(
    FooBarModel(foo='hello', bar={'whatever': 123}).model_dump(
        exclude_unset=True
    )
)
#> {'foo': 'hello', 'bar': {'whatever': 123}}
print(
    FooBarModel(banana=1.1, foo='hello', bar={'whatever': 123}).model_dump(
        exclude_defaults=True
    )
)
#> {'foo': 'hello', 'bar': {'whatever': 123}}
print(
    FooBarModel(foo='hello', bar={'whatever': 123}).model_dump(
        exclude_defaults=True
    )
)
#> {'foo': 'hello', 'bar': {'whatever': 123}}
print(
    FooBarModel(banana=None, foo='hello', bar={'whatever': 123}).model_dump(
        exclude_none=True
    )
)
#> {'foo': 'hello', 'bar': {'whatever': 123}}


class Model(BaseModel):
    x: List[Json[Any]]


print(Model(x=['{"a": 1}', '[1, 2]']).model_dump())
#> {'x': [{'a': 1}, [1, 2]]}
print(Model(x=['{"a": 1}', '[1, 2]']).model_dump(round_trip=True))
#> {'x': ['{"a":1}', '[1,2]']}
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L22-L27",
      "basis_source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "content_locator": "chars:140:543",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:b569808fe3e91c433d6d5b0d161fbde0e96719d5b91782ea94ef4bf5a23c02ee",
  "contributions": [
    {
      "content_end": 2320,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "source_locator": "L17-L97"
    }
  ],
  "curator_notes": "Pending human review. Full selected code block retained, including incidental JSON round_trip example; it is not a new benchmark topic.",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:ff1f3e3ee236ff1387cd370b65854454999d9ee70de571433c98a6e65aed1f1d",
  "section_path": [
    "docs/concepts/serialization.md",
    "`model.model_dump(...)`"
  ],
  "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
  "source_locator": "L17-L97",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 17,
      "last": 97,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "suffix": ""
    }
  ]
}
```

## v2-extra

Evidence ID: `evidence:7b7cf7427e97588af230e2fbe78f40e686c952b53e3f2b1b05757058020df09c`

Original sources (document versions are not applicability labels):

- `source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d`: [docs/concepts/models.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/models.md); snapshot 2.5.3; sha256:ef0fb3734042b6b36d7da69fb3f4801af6eae4285b447854ff4a287993c8f42c

Full assembled content, quoted as data:

````text
## Extra fields

By default, Pydantic models won't error when you provide data for unrecognized fields, they will just be ignored:

```py
from pydantic import BaseModel


class Model(BaseModel):
    x: int


m = Model(x=1, y='a')
assert m.model_dump() == {'x': 1}
```

If you want this to raise an error, you can achieve this via `model_config`:

```py
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra='forbid')


try:
    Model(x=1, y='a')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Model
    y
      Extra inputs are not permitted [type=extra_forbidden, input_value='a', input_type=str]
    """
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L1614-L1649",
      "basis_source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "content_locator": "chars:17:724",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:8ba3b894b8fefa829ab53f0e523a21a6b4eab667d4db1111bd3f41d3ff859c50",
  "contributions": [
    {
      "content_end": 724,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "source_locator": "L1612-L1649"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:7b7cf7427e97588af230e2fbe78f40e686c952b53e3f2b1b05757058020df09c",
  "section_path": [
    "docs/concepts/models.md",
    "Extra fields"
  ],
  "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
  "source_locator": "L1612-L1649",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 1612,
      "last": 1649,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "suffix": ""
    }
  ]
}
```

## v2-field-validators

Evidence ID: `evidence:5ed599d618c2a175889d935bc3f49c783f312ea2c927b24eadc9e72166b05bb6`

Original sources (document versions are not applicability labels):

- `source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633`: [docs/concepts/validators.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/validators.md); snapshot 2.5.3; sha256:0eb8d911ec997065bfe7bd82bfe94bf00ba2f687a92e00e5377b6d5b2e9d9d72

Full assembled content, quoted as data:

````text
## Field validators

??? api "API Documentation"
    [`pydantic.functional_validators.field_validator`][pydantic.functional_validators.field_validator]<br>

If you want to attach a validator to a specific field of a model you can use the `@field_validator` decorator.

```py
from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
)


class UserModel(BaseModel):
    id: int
    name: str

    @field_validator('name')
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()

    # you can select multiple fields, or use '*' to select all fields
    @field_validator('id', 'name')
    @classmethod
    def check_alphanumeric(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(v, str):
            # info.field_name is the name of the field being validated
            is_alphanumeric = v.replace(' ', '').isalnum()
            assert is_alphanumeric, f'{info.field_name} must be alphanumeric'
        return v


print(UserModel(id=1, name='John Doe'))
#> id=1 name='John Doe'

try:
    UserModel(id=1, name='samuel')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    name
      Value error, must contain a space [type=value_error, input_value='samuel', input_type=str]
    """

try:
    UserModel(id='abc', name='John Doe')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    id
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='abc', input_type=str]
    """

try:
    UserModel(id=1, name='John Doe!')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    name
      Assertion failed, name must be alphanumeric
    assert False [type=assertion_error, input_value='John Doe!', input_type=str]
    """
```

A few things to note on validators:

* `@field_validator`s are "class methods", so the first argument value they receive is the `UserModel` class, not an instance of `UserModel`. We recommend you use the `@classmethod` decorator on them below the `@field_validator` decorator to get proper type checking.
* the second argument is the field value to validate; it can be named as you please
* the third argument, if present, is an instance of `pydantic.ValidationInfo`
* validators should either return the parsed value or raise a `ValueError` or `AssertionError` (``assert`` statements may be used).
* A single validator can be applied to multiple fields by passing it multiple field names.
* A single validator can also be called on *all* fields by passing the special value `'*'`.

!!! warning
    If you make use of `assert` statements, keep in mind that running
    Python with the [`-O` optimization flag](https://docs.python.org/3/using/cmdline.html#cmdoption-o)
    disables `assert` statements, and **validators will stop working**.

!!! note
    `FieldValidationInfo` is **deprecated** in 2.4, use `ValidationInfo` instead.


If you want to access values from another field inside a `@field_validator`, this may be possible using `ValidationInfo.data`, which is a dict of field name to field value.
Validation is done in the order fields are defined, so you have to be careful when using `ValidationInfo.data` to not access a field that has not yet been validated/populated — in the code above, for example, you would not be able to access `info.data['id']` from within `name_must_contain_space`.
However, in most cases where you want to perform validation using multiple field values, it is better to use `@model_validator` which is discussed in the section below.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L303-L303",
      "basis_source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "content_locator": "chars:157:268",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    },
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L373-L383",
      "basis_source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "content_locator": "chars:1993:2996",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:cc3f77ff25cce63f901de0146ed4ae01374aeff705f3c757eb4fa99a1a7fbe38",
  "contributions": [
    {
      "content_end": 3730,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "source_locator": "L298-L391"
    }
  ],
  "curator_notes": "Pending human review. Incidental FieldValidationInfo deprecation note retained, but no claim about the intermediate 2.4 release is annotated.",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:5ed599d618c2a175889d935bc3f49c783f312ea2c927b24eadc9e72166b05bb6",
  "section_path": [
    "docs/concepts/validators.md",
    "Field validators"
  ],
  "source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
  "source_locator": "L298-L391",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 298,
      "last": 391,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "suffix": ""
    }
  ]
}
```

## v2-iteration

Evidence ID: `evidence:d92505ddf3dab1bc30ce5846bb6ff07b452d74c73a7257de03624d2bddc53e00`

Original sources (document versions are not applicability labels):

- `source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955`: [docs/concepts/serialization.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/serialization.md); snapshot 2.5.3; sha256:81c9d6d63677846feebdd0c5bc9770fa3a37078007468044b188dc988756da7e

Full assembled content, quoted as data:

````text
## `dict(model)` and iteration

Pydantic models can also be converted to dictionaries using `dict(model)`, and you can also iterate over a model's
fields using `for field_name, field_value in model:`. With this approach the raw field values are returned, so
sub-models will not be converted to dictionaries.

Example:

```py
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

print(dict(m))
#> {'banana': 3.14, 'foo': 'hello', 'bar': BarModel(whatever=123)}
for name, value in m:
    print(f'{name}: {value}')
    #> banana: 3.14
    #> foo: hello
    #> bar: whatever=123
```

Note also that [`RootModel`](models.md#rootmodel-and-custom-root-types) _does_ get converted to a dictionary with the key `'root'`.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L144-L146",
      "basis_source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "content_locator": "chars:32:308",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:58bec3e2cd9f47617b1c6e15b3e176c56e2a891a4a2f0fcfca547f79b4100820",
  "contributions": [
    {
      "content_end": 886,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "source_locator": "L142-L175"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:d92505ddf3dab1bc30ce5846bb6ff07b452d74c73a7257de03624d2bddc53e00",
  "section_path": [
    "docs/concepts/serialization.md",
    "`dict(model)` and iteration"
  ],
  "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
  "source_locator": "L142-L175",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 142,
      "last": 175,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "suffix": ""
    }
  ]
}
```

## v2-model-validate

Evidence ID: `evidence:7f401a00baab9c24c6506ed641ec655534f5cbec1fe540ba9cfe9de8f66c2301`

Original sources (document versions are not applicability labels):

- `source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d`: [docs/concepts/models.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/models.md); snapshot 2.5.3; sha256:ef0fb3734042b6b36d7da69fb3f4801af6eae4285b447854ff4a287993c8f42c

Full assembled content, quoted as data:

````text
## Helper functions

* [`model_validate()`][pydantic.main.BaseModel.model_validate]: this is very similar to the `__init__` method of the model, except it takes a dict or an object
  rather than keyword arguments. If the object passed cannot be validated, or if it's not a dictionary
  or instance of the model in question, a `ValidationError` will be raised.

```py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None


m = User.model_validate({'id': 123, 'name': 'James'})
print(m)
#> id=123 name='James' signup_ts=None

try:
    User.model_validate(['not', 'a', 'dict'])
except ValidationError as e:
    print(e)
    """
    1 validation error for User
      Input should be a valid dictionary or instance of User [type=model_type, input_value=['not', 'a', 'dict'], input_type=list]
    """
```

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: the retained User example documents model_validate dictionary-input usage at docs/concepts/models.md L443-L451, particularly the call at L449, proposed for 2.5.3 only. The displayed output is quoted documentation, not independently executed behavior. This does not assert that every dictionary input is valid or that all non-dictionary/non-model inputs are rejected. Human review remains pending.",
      "basis_locator": "L443-L451",
      "basis_source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "content_locator": "chars:476:682",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:9949b6f9050f3bb138ec14aa28212c514ac645b5d5613951a105fd18b776678c",
  "contributions": [
    {
      "content_end": 21,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "source_locator": "L427-L428"
    },
    {
      "content_end": 360,
      "content_start": 21,
      "role": "supporting_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "source_locator": "L431-L433"
    },
    {
      "content_end": 958,
      "content_start": 360,
      "role": "supporting_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "source_locator": "L435-L460"
    }
  ],
  "curator_notes": "Pending human review. Closing Markdown code fence inserted after the selected example; no model_validate_json content included.",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:7f401a00baab9c24c6506ed641ec655534f5cbec1fe540ba9cfe9de8f66c2301",
  "section_path": [
    "docs/concepts/models.md",
    "Helper functions"
  ],
  "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
  "source_locator": "L427-L428",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 427,
      "last": 428,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "suffix": ""
    },
    {
      "first": 431,
      "last": 433,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "suffix": ""
    },
    {
      "first": 435,
      "last": 460,
      "prefix": "",
      "role": "supporting_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "suffix": "```\n"
    }
  ]
}
```

## v2-nested-filter

Evidence ID: `evidence:f6f7fddb0625fd25e1f626799e80adcdaecdce0b25fcb829f01e735375425cae`

Original sources (document versions are not applicability labels):

- `source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955`: [docs/concepts/serialization.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/serialization.md); snapshot 2.5.3; sha256:81c9d6d63677846feebdd0c5bc9770fa3a37078007468044b188dc988756da7e

Full assembled content, quoted as data:

````text
## Advanced include and exclude

The `model_dump` and `model_dump_json` methods support `include` and `exclude` arguments which can either be
sets or dictionaries. This allows nested selection of which fields to export:

```py
from pydantic import BaseModel, SecretStr


class User(BaseModel):
    id: int
    username: str
    password: SecretStr


class Transaction(BaseModel):
    id: str
    user: User
    value: int


t = Transaction(
    id='1234567890',
    user=User(id=42, username='JohnDoe', password='hashedpassword'),
    value=9876543210,
)

# using a set:
print(t.model_dump(exclude={'user', 'value'}))
#> {'id': '1234567890'}

# using a dict:
print(t.model_dump(exclude={'user': {'username', 'password'}, 'value': True}))
#> {'id': '1234567890', 'user': {'id': 42}}

print(t.model_dump(include={'id': True, 'user': {'id'}}))
#> {'id': '1234567890', 'user': {'id': 42}}
```

The `True` indicates that we want to exclude or include an entire key, just as if we included it in a set.
This can be done at any depth level.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L497-L498",
      "basis_source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "content_locator": "chars:33:220",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:e7ac7a3683d824cea33e7c631f1e9fab9ef3b17ab013d13b3d03f278bfb3921c",
  "contributions": [
    {
      "content_end": 1034,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "source_locator": "L495-L535"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:f6f7fddb0625fd25e1f626799e80adcdaecdce0b25fcb829f01e735375425cae",
  "section_path": [
    "docs/concepts/serialization.md",
    "Advanced include and exclude"
  ],
  "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
  "source_locator": "L495-L535",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 495,
      "last": 535,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "suffix": ""
    }
  ]
}
```

## v2-nested-subclass

Evidence ID: `evidence:f7b5629735f7a4a5e01a76beab4f534816e11a77e6223d001a9f49ceed710c8e`

Original sources (document versions are not applicability labels):

- `source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955`: [docs/concepts/serialization.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/serialization.md); snapshot 2.5.3; sha256:81c9d6d63677846feebdd0c5bc9770fa3a37078007468044b188dc988756da7e

Full assembled content, quoted as data:

````text
### Subclass instances for fields of `BaseModel`, dataclasses, `TypedDict`

When using fields whose annotations are themselves struct-like types (e.g., `BaseModel` subclasses, dataclasses, etc.),
the default behavior is to serialize the attribute value as though it was an instance of the annotated type,
even if it is a subclass. More specifically, only the fields from the _annotated_ type will be included in the
dumped object:

```py
from pydantic import BaseModel


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    user: User


user = UserLogin(name='pydantic', password='hunter2')

m = OuterModel(user=user)
print(m)
#> user=UserLogin(name='pydantic', password='hunter2')
print(m.model_dump())  # note: the password field is not included
#> {'user': {'name': 'pydantic'}}
```
!!! warning "Migration Warning"
    This behavior is different from how things worked in Pydantic V1, where we would always include
    all (subclass) fields when recursively dumping models to dicts. The motivation behind this change in
    behavior is that it helps ensure that you know precisely which fields could be included when serializing,
    even if subclasses get passed when instantiating the object. In particular, this can help prevent surprises
    when adding sensitive information like secrets as fields of subclasses.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L395-L398",
      "basis_source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "content_locator": "chars:76:431",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    },
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L424-L429",
      "basis_source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "content_locator": "chars:848:1383",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:31bd82217029c58f26a2b962c6279f30838a4ce64f5edc9104f2f6f726be1b65",
  "contributions": [
    {
      "content_end": 1383,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "source_locator": "L393-L429"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:f7b5629735f7a4a5e01a76beab4f534816e11a77e6223d001a9f49ceed710c8e",
  "section_path": [
    "docs/concepts/serialization.md",
    "Serializing subclasses",
    "Subclass instances for fields of `BaseModel`, dataclasses, `TypedDict`"
  ],
  "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
  "source_locator": "L393-L429",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 393,
      "last": 429,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "suffix": ""
    }
  ]
}
```

## v2-required

Evidence ID: `evidence:4e15db8c4875996cdf78901e0dc7a415c9b6ee2457f6d638ce28b96c9b4a1373`

Original sources (document versions are not applicability labels):

- `source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d`: [docs/concepts/models.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/models.md); snapshot 2.5.3; sha256:ef0fb3734042b6b36d7da69fb3f4801af6eae4285b447854ff4a287993c8f42c

Full assembled content, quoted as data:

````text
## Required fields

To declare a field as required, you may declare it using just an annotation, or you may use `Ellipsis`/`...`
as the value:

```py
from pydantic import BaseModel, Field


class Model(BaseModel):
    a: int
    b: int = ...
    c: int = Field(...)
```

Where `Field` refers to the [field function](json_schema.md#field-customization).

Here `a`, `b` and `c` are all required. However, this use of `b: int = ...` does not work properly
with [mypy](../integrations/mypy.md), and as of **v1.0** should be avoided in most cases.

!!! note
    In Pydantic V1, fields annotated with `Optional` or `Any` would be given an implicit default of `None` even if no
    default was explicitly specified. This behavior has changed in Pydantic V2, and there are no longer any type
    annotations that will result in a field having an implicit default value.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L1319-L1335",
      "basis_source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "content_locator": "chars:20:543",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    },
    {
      "applies_to": [],
      "basis": "The quoted passage explicitly describes a V1/V2 change. Endpoint policy maps those release families only to selected 1.10.13 and 2.5.3; no intervening or future release claim.",
      "basis_locator": "L1337-L1340",
      "basis_source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "content_locator": "chars:544:862",
      "kind": "transition",
      "transition_source": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "1.10.13"
        }
      ],
      "transition_target": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ]
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:e828cefacc7df09c1f5af75a4ae24f47cca0dfb4ecc68e6d727db83d095027ef",
  "contributions": [
    {
      "content_end": 862,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "source_locator": "L1317-L1340"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:4e15db8c4875996cdf78901e0dc7a415c9b6ee2457f6d638ce28b96c9b4a1373",
  "section_path": [
    "docs/concepts/models.md",
    "Required fields"
  ],
  "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
  "source_locator": "L1317-L1340",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 1317,
      "last": 1340,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:5e1f0d63d88386df85842d93d2a20a3c0047012c4a957cbdaa2e02780dabaa0d",
      "suffix": ""
    }
  ]
}
```

## v2-sequence-filter

Evidence ID: `evidence:d72bdda37f9d3c26b38333eb7b8715f7db7ec9e7d80897904b014a3dcc6b61b0`

Original sources (document versions are not applicability labels):

- `source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955`: [docs/concepts/serialization.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/serialization.md); snapshot 2.5.3; sha256:81c9d6d63677846feebdd0c5bc9770fa3a37078007468044b188dc988756da7e

Full assembled content, quoted as data:

````text
Special care must be taken when including or excluding fields from a list or tuple of submodels or dictionaries.
In this scenario, `model_dump` and related methods expect integer keys for element-wise inclusion or exclusion.
To exclude a field from **every** member of a list or tuple, the dictionary key `'__all__'` can be used, as shown here:

```py
import datetime
from typing import List

from pydantic import BaseModel, SecretStr


class Country(BaseModel):
    name: str
    phone_code: int


class Address(BaseModel):
    post_code: int
    country: Country


class CardDetails(BaseModel):
    number: SecretStr
    expires: datetime.date


class Hobby(BaseModel):
    name: str
    info: str


class User(BaseModel):
    first_name: str
    second_name: str
    address: Address
    card_details: CardDetails
    hobbies: List[Hobby]


user = User(
    first_name='John',
    second_name='Doe',
    address=Address(
        post_code=123456, country=Country(name='USA', phone_code=1)
    ),
    card_details=CardDetails(
        number='4212934504460000', expires=datetime.date(2020, 5, 1)
    ),
    hobbies=[
        Hobby(name='Programming', info='Writing code and stuff'),
        Hobby(name='Gaming', info='Hell Yeah!!!'),
    ],
)

exclude_keys = {
    'second_name': True,
    'address': {'post_code': True, 'country': {'phone_code'}},
    'card_details': True,
    # You can exclude fields from specific members of a tuple/list by index:
    'hobbies': {-1: {'info'}},
}

include_keys = {
    'first_name': True,
    'address': {'country': {'name'}},
    'hobbies': {0: True, -1: {'name'}},
}

# would be the same as user.model_dump(exclude=exclude_keys) in this case:
print(user.model_dump(include=include_keys))
"""
{
    'first_name': 'John',
    'address': {'country': {'name': 'USA'}},
    'hobbies': [
        {'name': 'Programming', 'info': 'Writing code and stuff'},
        {'name': 'Gaming'},
    ],
}
"""

# To exclude a field from all members of a nested list or tuple, use "__all__":
print(user.model_dump(exclude={'hobbies': {'__all__': {'info'}}}))
"""
{
    'first_name': 'John',
    'second_name': 'Doe',
    'address': {
        'post_code': 123456,
        'country': {'name': 'USA', 'phone_code': 1},
    },
    'card_details': {
        'number': SecretStr('**********'),
        'expires': datetime.date(2020, 5, 1),
    },
    'hobbies': [{'name': 'Programming'}, {'name': 'Gaming'}],
}
"""
```

The same holds for the `model_dump_json` method.


````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L537-L539",
      "basis_source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "content_locator": "chars:0:345",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:e7b3792a72f0d1687016306fe8a4c119fc0dbd7a58d4a4cd4582fdffbf66c862",
  "contributions": [
    {
      "content_end": 2485,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "source_locator": "L537-L638"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:d72bdda37f9d3c26b38333eb7b8715f7db7ec9e7d80897904b014a3dcc6b61b0",
  "section_path": [
    "docs/concepts/serialization.md",
    "Advanced include and exclude"
  ],
  "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
  "source_locator": "L537-L638",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 537,
      "last": 638,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:8ef3fd8a16591505025f689b7d6b3f99da3f6dd631138c9704c7b590155e5955",
      "suffix": ""
    }
  ]
}
```

## v2-validator-errors

Evidence ID: `evidence:a9c73c27473d19d0472e7ebb2f5a313950f5cc6ce9c5b3100f9aff1a5ece31ff`

Original sources (document versions are not applicability labels):

- `source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633`: [docs/concepts/validators.md](https://github.com/pydantic/pydantic/blob/9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4/docs/concepts/validators.md); snapshot 2.5.3; sha256:0eb8d911ec997065bfe7bd82bfe94bf00ba2f687a92e00e5377b6d5b2e9d9d72

Full assembled content, quoted as data:

````text
## Handling errors in validators

As mentioned in the previous sections you can raise either a `ValueError` or `AssertionError` (including ones generated by `assert ...` statements) within a validator to indicate validation failed.
You can also raise a `PydanticCustomError` which is a bit more verbose but gives you extra flexibility.
Any other errors (including `TypeError`) are bubbled up and not wrapped in a `ValidationError`.

````

Provenance and proposed applicability:

```json
{
  "applicability": [
    {
      "applies_to": [
        {
          "kind": "exact",
          "lower": null,
          "lower_inclusive": null,
          "open_bound_basis": null,
          "scheme": "pep440",
          "upper": null,
          "upper_inclusive": null,
          "value": "2.5.3"
        }
      ],
      "basis": "Endpoint policy: an unqualified behavior statement in this exact release documentation is proposed for 2.5.3 only. Historical qualifiers and deprecated compatibility are retained; documentation is evidence, not runtime verification.",
      "basis_locator": "L470-L472",
      "basis_source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "content_locator": "chars:34:432",
      "kind": "behavior",
      "transition_source": [],
      "transition_target": []
    }
  ],
  "assembly_policy": "explicit-lines-v1",
  "content_hash": "sha256:496e622403adb6760b0106f9fef52e02984f9321ca0ef3d35d3d7c8fb8bfc801",
  "contributions": [
    {
      "content_end": 432,
      "content_start": 0,
      "role": "primary_explanation",
      "source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "source_locator": "L468-L472"
    }
  ],
  "curator_notes": "Pending human review. ",
  "ecosystem_id": "pypi:pydantic",
  "evidence_id": "evidence:a9c73c27473d19d0472e7ebb2f5a313950f5cc6ce9c5b3100f9aff1a5ece31ff",
  "section_path": [
    "docs/concepts/validators.md",
    "Handling errors in validators"
  ],
  "source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
  "source_locator": "L468-L472",
  "technical_identifiers": []
}
```

Declared source assembly and marker replacements:

```json
{
  "includes": [],
  "parts": [
    {
      "first": 468,
      "last": 472,
      "prefix": "",
      "role": "primary_explanation",
      "source_id": "source:52b13daa1b59dd62db3a77845294d6c52cc2936b983ebf704d9e9a7b82787633",
      "suffix": ""
    }
  ]
}
```
