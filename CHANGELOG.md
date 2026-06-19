# Changelog

## [2.2.0](https://github.com/MailGlyph/mailglyph-python/compare/v2.1.0...v2.2.0) (2026-06-19)


### Features

* Email validation ([cd7b23a](https://github.com/MailGlyph/mailglyph-python/commit/cd7b23a8c51905ff22871930c1b110f4fafb715c))

## [2.1.0](https://github.com/MailGlyph/mailglyph-python/compare/v2.0.0...v2.1.0) (2026-03-26)


### Features

* add Templates resource and update OpenAPI spec with enhanced schemas for Contacts, Templates, and Campaigns ([fd8d717](https://github.com/MailGlyph/mailglyph-python/commit/fd8d717ea47be122cff4ddc9294acaf7e1baac05))

## [Unreleased]

### ⚠ BREAKING CHANGES

* Align list response shapes with OpenAPI: `contacts.list()` now returns records in `page.data` (not `page.contacts`).
* `campaigns.send()` now returns a typed `SendCampaignResult` with `success`, `data`, and `message`.

### Bug Fixes

* Match `GET /contacts` response parsing to `{ data, cursor, hasMore, total }`.
* Add Templates resource and support `GET /templates` pagination shape `{ data, total, page, pageSize, totalPages }`.
* Update `Contact`, `Template`, and `Segment` models to current OpenAPI schema fields and nullability.

## [2.0.0](https://github.com/MailGlyph/mailglyph-python/compare/v1.0.1...v2.0.0) (2026-03-09)


### ⚠ BREAKING CHANGES

* Renames the SDK/package branding from Mailrify to MailGlyph.

### Features

* Add `text` field to email sending parameters. ([cf7ae10](https://github.com/MailGlyph/mailglyph-python/commit/cf7ae10cf0bbcc4c79e80f38b75039a00973b367))
* Implement methods to add and remove contacts from static segments, along with supporting types and documentation. ([03b99ee](https://github.com/MailGlyph/mailglyph-python/commit/03b99ee87396e41c6bc5d758ae6bad8f0c5d4c33))


### Code Refactoring

* rebrand Mailrify to MailGlyph ([431caad](https://github.com/MailGlyph/mailglyph-python/commit/431caadd0eedeed19e77c01ec453005bafe2d9dd))

## [1.0.1](https://github.com/MailGlyph/mailglyph-python/compare/v1.0.0...v1.0.1) (2026-02-16)


### Documentation

* Add CI, Release Please, and PyPI publish badges to the README. ([a02f30b](https://github.com/MailGlyph/mailglyph-python/commit/a02f30b6b5ece8a2c52534794ef1a1ed9304ac8a))

## [1.0.0](https://github.com/MailGlyph/mailglyph-python/compare/v0.0.4...v1.0.0) (2026-02-16)


### ⚠ BREAKING CHANGES

* complete API redesign, not compatible with 0.1.x

### Features

* initial SDK implementation ([b067d32](https://github.com/MailGlyph/mailglyph-python/commit/b067d3288a77cfc120683bc8a34adb0c0f8dbe4d))


### Bug Fixes

* support pydantic type evaluation on python 3.9 ([9237800](https://github.com/MailGlyph/mailglyph-python/commit/9237800485f326acbe03d682f64ccc41883ccb4d))

## Changelog

All notable changes to this project will be documented in this file.
