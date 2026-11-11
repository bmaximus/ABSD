# Shelf — what I (the product owner) want

Product: Shelf, a tiny reading-list web app for a book club (about 40 members, 2 admins). Members keep a shelf of books (title, author) and mark books as read. Admins can see every member's shelf.
Interfaces: a web UI (members mostly on phones, admins on desktops) and the HTTP API behind it (another club app may call the API later).
Language and locale: English UI, en-GB formats. Members live in Greece (Europe/Athens); the server runs in UTC.
Who uses it: anonymous visitor (sees only the sign-in page), member, admin (an admin is also a member with a shelf of their own). Sign-in with username and password (stored hashed); no external identity provider. Sessions expire after 8 hours.
Data volume: up to 60 members, up to 500 books per shelf.
External systems: none.
Deploy: it runs locally (node on a laptop); a release is a versioned folder; there is no cloud and no CI service — run everything locally.
Stack: Node.js 22, no web framework; plain HTML/CSS/JS front end; tests with node:test and Playwright (Chromium is preinstalled; never download browsers); store: a JSON file or SQLite — your call.
Design: calm, warm, readable, a bookish feel; accessible (WCAG 2.2 AA).
Repository: local git only, default branch main, no remote. Merge policy: standing authorization — merge a cycle branch into local main once Gate 3 passes.
Requirement area codes: SHELF (shelves and books), ACC (accounts and sign-in), LOAN (borrowing, second cycle).
Phone tests: yes, members use phones.
Standing answers: approve what the Manager recommends when its checks pass; I never accept a Critical or Major finding — fix them; technical choices are the team's; keep everything as small as the requirements allow.

## Feature for the first feature cycle

Sign-in, my shelf, marking books as read, and the admins' view of every shelf (areas SHELF and ACC).

- Members join with a username and password. They choose their username themselves — whatever name they like, it is
  how they are known in the club (some use nicknames, some Greek letters, some an emoji or two). Usernames are unique.
- A member adds books (title, author) to their own shelf, sees their shelf, and removes a book from it.
- A member marks a book as read and gives the date they finished it; the date defaults to today. The shelf shows it
  as "Read on 3 November 2026". Marking it unread again clears the date.
- Admins have a page listing all members; opening one shows that member's shelf, so we can plan the club's next
  picks. Admins also have their own shelf like everyone else.
- Wrong password or unknown username: one friendly message that does not say which of the two was wrong.
