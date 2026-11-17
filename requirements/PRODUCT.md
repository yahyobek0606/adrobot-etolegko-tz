# Product

A wrapper over the Keitaro ad tracker. The original assignment is in [tz.md](tz.md); this file turns it into user stories and records the decisions made where it is ambiguous.

Provider service = Keitaro in this case.

## User stories

### Campaign list
- Given the user opens the website, they see a list of campaigns from the provider with a "New campaign" button
- Clicking a campaign opens its editor

### Campaign creator
- Given the user clicks "New campaign", a form is displayed with: Name, Geo, Offer, Domain, Group, Source
- Offer field has autocomplete with live search over provider offers
- On "Create", a campaign is created in the provider with two streams:
  1. Fallback stream: country filter = Geo (accept), redirects to Google
  2. Offer stream: sends traffic to the selected offer with 100% share
- After creation the user is redirected to the campaign editor

### Campaign editor
- Given the user opens a campaign, they see the offers table of the offer stream
- The table has headers: Offer, Share (%), Action (delete button)
- The user can add a new item: clicking "Add" opens a dialog
- While typing in the dialog, the app does a live search for offers by name in the provider
- When the table has changes, an indicator alerts the user about unsaved changes, and two buttons become enabled: "Push Changes" and "Cancel"
- Each share has a "Pin" toggle. Clicking it pins or unpins the share percentage
  - Example: 4 items at 25% each, two of them pinned. If items are later added or removed, the pinned items keep 25%
- If the user deletes an item, it is marked as archived. On push it is deleted from the provider but kept archived in this service. Archived rows show a "Restore" button
- The header has "Fetch Streams From KT" and "View in KT" buttons
- If an offer was deleted directly in the provider, "Fetch Streams From KT" syncs local data with the provider

## Assumptions
Decisions made where the spec was ambiguous. Change them here if they are wrong.

1. **Geo** — one or more ISO 3166-1 alpha-2 country codes (e.g. `MX,AU,RO`), all go into a single country filter of the fallback stream.
2. **Domain, group, source** — dropdowns loaded from the provider, preselected with defaults from env (`KEITARO_DEFAULT_*`).
3. **Fallback URL** — configurable via `FALLBACK_REDIRECT_URL`, default `https://google.com`.
4. **Stream order** — the fallback stream goes first, the offer stream second, campaign rotation is by position.
5. **Shares are integers** — provider weights are whole percentages.
6. **Share calculation**
   - Only active (non-archived) offers take part
   - Pinned offers keep their value
   - The remainder `100 - sum(pinned)` is split evenly among unpinned offers
   - The rounding leftover goes +1% to unpinned offers in table order, top to bottom
   - Example: 3 unpinned offers, remainder 100 → 34, 33, 33
7. **Manual share edit** — the user can type a share value; editing a share automatically pins it.
8. **Validation** — Push Changes is disabled, with an error shown, when:
   - pinned shares sum to more than 100, or
   - all offers are pinned and the total is not 100, or
   - there are no active offers
9. **Deferred changes** — add, delete, restore, pin and edit are local drafts. Nothing reaches the provider until "Push Changes". "Cancel" discards the draft.
10. **Restore** — a restored offer comes back unpinned and is included in the share recalculation.
11. **Fetch from provider**
    - If there are unpushed changes, the user must confirm discarding them first
    - Offers present locally but missing in the provider become archived
    - Offers present in the provider but missing locally are added
    - Shares are taken from the provider
12. **View in KT** — opens the campaign page in the Keitaro admin in a new tab.
13. **Auth** — none. This is a single-user internal tool.
