# Transparent Domains Design

## Goal

ComboCode must not force a goal into one exclusive drawer. A goal can remain stored once while being visible from every domain it belongs to.

The concrete regression is `opera://settings/keyboardShortcuts`: its primary category is `Browser url's`, but it is also an Opera resource and therefore must be discoverable when the user filters `Browser · Opera`.

## Data model

Keep the existing scalar `category` field as the primary/display category for backward compatibility.

Add an optional `domains` array of strings to any goal. A goal belongs to the union of:

- its primary `category`;
- every value in `domains`.

No goal is duplicated physically.

## Engine behavior

`KnowledgeBase.categories()` returns the union of primary categories and additional domains.

`KnowledgeBase.search(query, category=...)` accepts a goal when the selected category matches either the primary category or one of its additional domains.

The search scoring algorithm remains unchanged. Additional domains are indexed in the searchable blob so domain names remain meaningful search context.

`route_rows()` inherits the same transparent-domain behavior through `search()`.

## Initial data mapping

Every goal in `browser_internal_urls.json` belongs to both:

- `Browser url's` as primary category;
- `Browser · Opera` as an additional domain.

This makes Opera's internal pages visible from the Opera domain without removing them from the internal-URL domain.

## Compatibility

Existing packs without `domains` continue to behave exactly as before.

The UI continues to display the primary `category` in its category column. Transparent domains affect discovery/filtering, not physical duplication or display identity.

## Acceptance criteria

- Filtering `Browser · Opera` and searching `shortcut` includes the goal whose route is `opera://settings/keyboardShortcuts`.
- Filtering `Browser url's` still includes that same goal.
- `Browser · Opera` remains available as a category.
- Existing category-only goals continue to filter exactly as before.
- Goal IDs remain unique.
