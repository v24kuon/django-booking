| Case ID | Input / Precondition | Perspective (Equivalence / Boundary) | Expected Result | Notes |
|---|---|---|---|---|
| TC-AUTH-01 | Register: valid email, password(>=8), role=stallholder | Equivalence – normal | User created and stallholder_profile created | - |
| TC-AUTH-02 | Register: email="" | Boundary – empty | Validation error (email required) | - |
| TC-AUTH-03 | Register: email without "@" | Equivalence – invalid format | Validation error (email format) | - |
| TC-AUTH-04 | Register: password length 7 | Boundary – min-1 | Validation error (password too short) | Min length=8 |
| TC-AUTH-05 | Register: duplicate email | Equivalence – duplicate | Validation error (email already exists) | Unique constraint |
| TC-AUTH-06 | Login: correct email/password | Equivalence – normal | Authentication succeeds | - |
| TC-AUTH-07 | Login: wrong password | Equivalence – invalid | Authentication fails | - |
| TC-AUTH-08 | Login: user is_active=false | Equivalence – invalid | Authentication blocked | - |
| TC-AUTH-09 | Register: email=NULL | Boundary – NULL | Validation error (email required) | - |
| TC-AUTH-10 | Register: role=admin (public registration) | Equivalence – invalid | Validation error (admin not allowed) | 管理者はシード作成のみ |
| TC-AUTH-11 | Register: password length 73 bytes | Boundary – max+1 | Validation error (password too long) | Max=72 bytes |
| TC-EVT-01 | Organizer creates event with valid dates/capacity | Equivalence – normal | Event created with status draft | Max値未定のため未検証 |
| TC-EVT-02 | Create event: capacity=0 | Boundary – 0 | Validation error (capacity) | Min=1 |
| TC-EVT-03 | Create event: end_date < start_date | Boundary – -1 | Validation error (date order) | - |
| TC-EVT-04 | Create event: application_deadline > start_date | Boundary – invalid | Validation error (deadline) | - |
| TC-ORG-01 | Organizer edits own draft event | Equivalence – normal | Event updated | - |
| TC-ORG-02 | Organizer edits event not owned | Equivalence – invalid | Authorization error | - |
| TC-ORG-03 | Organizer edits non-draft event | Equivalence – invalid | Validation error (not editable) | - |
| TC-ORG-04 | Organizer submits own draft event | Equivalence – normal | Event status becomes pending_review | - |
| TC-ORG-05 | Organizer submits event not owned | Equivalence – invalid | Authorization error | - |
| TC-ORG-06 | Organizer submits non-draft event | Equivalence – invalid | Validation error (status) | - |
| TC-ST-01 | Search events by region | Equivalence – normal | Only matching region events shown | - |
| TC-ST-02 | Search events by genre | Equivalence – normal | Only matching genre events shown | - |
| TC-ST-03 | Search events by date | Equivalence – normal | Events covering selected date shown | - |
| TC-ST-04 | Update stallholder profile | Equivalence – normal | Profile updated | - |
| TC-ST-05 | Update profile with non-stallholder | Equivalence – invalid | Authorization error | - |
| TC-APP-01 | Stallholder applies to open event | Equivalence – normal | Application created | - |
| TC-APP-02 | Stallholder applies to draft event | Equivalence – invalid | Validation error (event not open) | - |
| TC-APP-03 | Stallholder applies twice to same event | Equivalence – duplicate | Validation error (duplicate application) | Unique constraint |
| TC-APP-04 | Organizer attempts to apply | Equivalence – invalid role | Authorization error | 1 user = 1 role |
| TC-APP-05 | Organizer approves application for own event | Equivalence – normal | Application status becomes approved | - |
| TC-APP-06 | Organizer approves application for other organizer | Equivalence – invalid | Authorization error | - |
| TC-APP-07 | Stallholder cancels own pending application | Equivalence – normal | Application status becomes cancelled | - |
| TC-APP-08 | Stallholder cancels application not owned | Equivalence – invalid | Authorization error | - |
| TC-APP-09 | Stallholder cancels already rejected application | Equivalence – invalid | Validation error (not cancellable) | - |
| TC-NOTIF-01 | Application submitted | Equivalence – normal | Organizer notification created | - |
| TC-NOTIF-02 | Message sent | Equivalence – normal | Recipient notification created | - |
| TC-NOTIF-03 | Event updated (open status) | Equivalence – normal | Approved applicants notified | - |
| TC-NOTIF-04 | Event review result | Equivalence – normal | Organizer notified | - |
| TC-NOTIF-05 | Review posted | Equivalence – normal | Target user notified | - |
| TC-NOTIF-06 | Low rating review (<=2) | Equivalence – normal | Organizer notified | - |
| TC-NOTIF-07 | Application cancelled | Equivalence – normal | Organizer notified | - |
| TC-ADM-01 | Admin approves pending_review event | Equivalence – normal | Event status becomes open | - |
| TC-ADM-02 | Admin approves event not pending_review | Equivalence – invalid | Validation error (status) | - |
| TC-ADM-03 | Admin approves stallholder profile | Equivalence – normal | review_status becomes approved | - |
| TC-ADM-04 | Admin updates report status | Equivalence – normal | report status updated | - |
| TC-MSG-01 | Send message with approved application | Equivalence – normal | Message created | - |
| TC-MSG-02 | Send message with pending application | Equivalence – invalid | Validation error (not approved) | - |
| TC-MSG-03 | Send message with empty content | Boundary – empty | Validation error (content required) | - |
| TC-REV-01 | Submit review once per application/author | Equivalence – normal | Review created | - |
| TC-REV-02 | Submit duplicate review | Equivalence – duplicate | Validation error (duplicate review) | Unique constraint |
| TC-REV-03 | Submit review with score=0 | Boundary – 0 | Validation error (score invalid) | Min=1 |
