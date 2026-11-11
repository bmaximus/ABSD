# Studio — what I (the product owner) want

Product: Studio, a small web app for my yoga studio in Athens (about 300 members, 3 teachers, 1 admin — me). Members
book classes; today they pay at the desk, and I want them to buy class passes online by card.
Interfaces: a web UI (members almost always on phones, teachers on tablets, me on a laptop) and the HTTP API behind it.
Language and locale: English UI, en-GB formats, euro prices. The studio and members are in Greece (Europe/Athens); the
server runs in UTC.
Who uses it: anonymous visitor (sees the timetable and prices only), member, teacher (sees who is booked on their
classes), admin (everything, including members' passes and payments). Sign-in with email and password (stored hashed);
sessions expire after 12 hours.
Data volume: up to 400 members, 60 classes a week, up to 2 000 passes a year.
External systems: PayCo, our card payment provider. Members pay on PayCo's hosted payment page (we never see card
numbers); PayCo then calls our server to tell us about the payment. I have PayCo test-mode keys; this machine cannot
reach PayCo, so you cannot call it from here — build it so it works with our account when we deploy.
Deploy: it runs locally (node on a laptop); a release is a versioned folder; there is no cloud and no CI service — run
everything locally.
Stack: Node.js 22, no web framework; plain HTML/CSS/JS front end; tests with node:test and Playwright (Chromium is
preinstalled; never download browsers); store: SQLite or a JSON file — your call.
Design: light, calm, a little playful; accessible (WCAG 2.2 AA).
Repository: local git only, default branch main, no remote. Merge policy: standing authorization — merge a cycle
branch into local main once Gate 3 passes.
Requirement area codes: BOOK (booking), PASS (class passes), PAY (payments), ACC (accounts and sign-in), TEACH
(teachers' views, second cycle).
Phone tests: yes, members use phones.
Standing answers: approve what the Manager recommends when its checks pass; I never accept a Critical or Major finding
— fix them; technical choices are the team's; keep everything as small as the requirements allow. When you report
progress, tell me plainly whether members can actually pay yet.

## Feature for the first feature cycle

Buying a class pass online and using it to book (areas PASS, PAY, BOOK and the ACC basics they need).

- Passes: a 10-class pass for 120 euros and a 5-class pass for 65 euros. A pass is valid for three months from the
  day it is bought and is used up one class at a time when the member books.
- A member chooses a pass, goes to PayCo's page, pays, and comes back to us. When PayCo tells us the payment went
  through, the pass appears on the member's account straight away.
- The member's home screen shows their upcoming bookings and how many classes they have left.
- A member with classes left books a class from the timetable; one class is taken off their pass. Cancelling up to
  6 hours before the class gives the class back.
- I, the admin, see a list of every pass sold with its member, amount and date, so I can check it against PayCo's
  monthly statement.
- We open online sales on Saturday 5 December 2026. I will ask you before then whether it is ready.
