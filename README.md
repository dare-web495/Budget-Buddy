Budget Buddy: Localized Asynchronous Envelope Budgeting & Portfolio Advisory Engine

Project Description:
 Budget Buddy is a production-grade personal finance engineering web application specifically architected for 
 the Kenyan economic ecosystem. Moving beyond the limitations of standard passive ledgers, this application 
 implements a strict, real-time programmatic enforcement of the traditional "envelope budgeting" financial 
 framework. Users initialize their workflow by declaring a localized monthly income pool denominated in 
 Kenyan Shillings (KES). From this master pool, users provision distinct, ring-fenced virtual budget slices 
 or "envelopes" assigned to custom operational titles across three main financial vectors: Core Needs 
 (Expenses), Lifestyle Choices (Wants), and Future Allocations (Savings).

 The application operates as an event-driven single-page dashboard for daily interactions, utilizing an 
 asynchronous JavaScript (AJAX) engine to log specific daily transaction data. Transactions automatically 
 cross-reference open envelopes, deduct balances from relevant targets, compute multi-tiered spending 
 velocities, and track data trends on the fly.

 To transition the web platform from a standard data entry logger into an active intelligent platform, Budget 
 Buddy features a custom algorithmic Advisory Pipeline. By directly overriding Django’s native authentication 
 model, the platform embeds a behavioral financial profile into the user's account entity. It calculates 
 individual risk tolerances (LOW, MED, HIGH) and securely maps unallocated capital surpluses to actual 
 localized investment vectors available in the Kenyan market—ranging from highly secure Central Bank of Kenya 
 (CBK) Treasury Bills and M-Akiba infrastructure bonds, to intermediate Money Market Funds (MMFs), up to 
 high-yield Nairobi Securities Exchange (NSE) equities and digital crypto assets.

Distinctiveness and Complexity.
 Architectural Distinctiveness from Course Curriculum:
 Budget Buddy diverges fundamentally from the standard structural blueprints provided across all prior CS50W 
 projects, including Wiki, Commerce, Pizza, and Network.

 Standard course assignments rely heavily on unbounded, linear chronological structures. For example, the 
 Network assignment processes flat timelines of user posts, and Commerce relies on basic relational auctions. 
 Budget Buddy, by contrast, enforces strict temporal and numerical isolation boundaries. Financial ledger 
 states are algorithmically boxed into specific calendar month and year frames (month_year). The platform 
 forces separate database models to interact synchronously across shifting monthly accounting boundaries, 
 creating a unique data lifecycle.

 Furthermore, the application implements a unique, closed-loop financial feedback mechanism. Rather than 
 executing standard, isolated CRUD actions where an object is created and forgotten, Budget Buddy operates on 
 a relational data balance architecture. The system features a multi-form ledger modification hub that 
 handles transactional cancellations, individual budget alterations, and full income modifications 
 concurrently.
 
 Most importantly, the platform distinguishes itself by incorporating an embedded regional investment advice 
 system. Linking a custom user profile's risk-appetite metadata directly to a dynamic structural table of 
 localized market assets (like M-Akiba and CBK Treasury instruments) moves the platform entirely away from a 
 standard social network or static warehouse log. It introduces an specialized layer of personalized 
 calculations completely unseen in any default class syllabus.

Technical Complexity and Engineering Defense:
 The technical complexity of Budget Buddy is established across its normalized relational database safety 
 constraints, complex background aggregation algorithms, and single-page asynchronous communication layer.

 1. Relational Integrity at the Database Schema Layer
  Data corruption in financial applications represents a catastrophic failure state. To guarantee total 
  accounting accuracy, the platform handles logic enforcement directly within the SQL database management 
  layer using Django's Meta constraints. By declaring unique_together attributes on the IncomePool model 
  (user, month_year) and the BudgetAllocation model (pool, category), the database structurally blocks 
  invalid data entry. It is impossible for programmatic race conditions or faulty client-side scripts to 
  duplicate a monthly income pool or register overlapping category slices within the same accounting cycle.

 2. Complex In-Memory Data Synthesizers and Algorithmic Inference
  The analytical heart of the application is the monthly_summary endpoint. Rather than wasting server disk 
  space or risking stale cache states by saving updating metrics inside a model field, this controller builds 
  volatile computational summaries in memory during runtime. It performs cross-table query aggregations using 
  Django's backend engine, isolating data points by calendar months, separating Needs from Wants, calculating 
  remaining unallocated capital, and structuring localized arrays of recent ledger items.

  Furthermore, inside add_transaction, the backend runs an automated classification algorithm. When an 
  expense is recorded via the UI, the backend intercepts the text description, matches it against active 
  BudgetAllocation models for that specific timeframe, and automatically infers the high-level category 
  (EXPENSE, WANT, or SAVING), reducing input steps for the user while protecting data categorization.
 
 3. Event-Driven Asynchronous JavaScript Engine
  The primary user interface operates completely free of traditional page-refresh patterns. It relies on a 
  custom JavaScript execution model built over native browser APIs. Forms do not use default submissions; 
  instead, event listeners trap user interactions, serialize records into raw JSON packets, and manage 
  background data transfers via the browser's Fetch API.
 
  The script features a centralized client state loop (updateDashboardData) that acts as a continuous 
  frontend updater. It queries API endpoints, parses data responses, applies clean regional financial 
  formatting using JavaScript's native internationalization wrapper (Intl.NumberFormat('en-KE')), and handles 
  dynamic changes like archiving depleted envelopes and managing browser storage states via sessionStorage 
  token throttling to prevent alert spamming.

What’s Contained in Each File Created:
 This web application maintains a clean, highly structured separation of concerns between its 
 object-relational storage layers, server controllers, routing protocols, client-side dynamic runtimes, and 
 user interfaces.

 Backend Django Application Modules:
  models.py: Configures the relational state architecture. It overrides Django’s core authorization table by 
  subclassing AbstractUser to inject custom profile attributes (risk_tolerance and preferred_currency) 
  directly into the master authentication record. It establishes the foreign key mappings, delete mechanics, 
  and database constraints for IncomePool, BudgetAllocation, Transaction, and InvestmentOption.
  
  views.py: The central operational controller engine of the application. It contains traditional template 
  rendering routers alongside asynchronous API endpoints (add_income, add_allocation, add_transaction, 
  delete_account). It handles parsing variations, dates validation catch blocks, strict login_required access 
  isolation, and in-memory aggregation matrices within monthly_summary.
  
  urls.py: Defines the URL routing matrix. It maps operational URL patterns to their respective controller 
  hooks, establishes namespaced internal routes, handles class-based user session states (such as redirecting 
  authenticated profiles directly past login inputs), and features strict type-safe parameter catch filters 
  like <int:year>/<int:month>/ for monthly ledgers.
  
  forms.py: Configures custom server-side data extraction components. It extends the native Django 
  UserCreationForm to explicitly map additional fields (email, risk_tolerance) into the user onboarding 
  workflow. It overrides the initialization method (__init__) to programmatically inject standard responsive 
  styling classes directly into the HTML widget array during rendering.

 Frontend Application Templates & Interface Controllers:
  script.js: The driver of the frontend experience. It securely manages extraction of cross-site request 
  forgery (csrftoken) values from cookies, captures submission interactions, processes JSON exchanges with 
  the backend, applies local currency layouts, and manipulates dashboard DOM elements dynamically. 

  index.html: The dynamic landing dashboard interface. Extending the master platform boilerplate, it 
  implements template-level conditional checks ({% if not current_pool %}) to switch seamlessly between a 
  clear onboarding screen for new tracking periods and a multi-card metrics array for ongoing accounting 
  cycles.
 
  manage_finance.html: The backend ledger management panel. It provides users with an administrative hub, 
  compiling nested, loop-generated form groups ({% for alloc in allocations %}) that link item-specific 
  editing, numerical value adjustments, and secure individual item deletions directly to a centralized 
  control endpoint.
 
  layout.html: The master structural shell template. It configures the overall standard HTML5 webpage layout, 
  controls device responsive viewports, sets up navigation items, and manages global imports of third-party 
  styling frameworks and core UI scripts.
 
  login.html & register.html: Core security interfaces. These clean templates extend the global layout file 
  to handle user entry and profile onboarding using responsive form elements.

How to Run the Application:
 Follow these step-by-step instructions to provision, configure, and launch the Budget Buddy engine within a 
 local development environment:
 
  1. Clone the Source Repository
   Download the project files locally and navigate into the root directory of the application: 

    git clone <your-repository-url>
    cd <project-folder-name>

  2. Initialize a Clean Virtual Environment 
   Isolate the application's runtime dependencies from your global system environment:

    python -m venv venv

    Activate the isolated environment based on your current operating system platform:
    macOS / Linux: source venv/bin/activate
    Windows (Command Prompt): venv\Scripts\activate.bat
    Windows (PowerShell): .\venv\Scripts\Activate.ps1

  3. Install Required System Dependencies
   Leverage the python package manager to read the requirements file and install the application framework:

    pip install -r requirements.txt

  4. Execute Database Migrations
   Compile and apply the object-relational model maps to generate your localized SQLite database file:
    
    python manage.py makemigrations
    python manage.py migrate

  5. Boot Up the Local Development Web Server
   Launch Django's development engine to begin handling HTTP requests:
    
    python manage.py runserver

  6. Access the Running Platform Web Interface
   Open any modern browser and navigate to the local hosting address:

    http://127.0.0
    
Additional Information
 Regional Financial Localization Standards:
  Budget Buddy is strictly designed around Kenyan economic conditions. All financial numbers, values, and 
  calculations map directly to the Kenyan Shilling currency standard (KES). Client interfaces format 
  accounting values using JavaScript's native internationalization wrapper (en-KE), ensuring that currency 
  notations match standard local formats.

 Security Mechanisms and Session Protection
  The application features explicit cross-site vulnerability protections. Every state-altering API request 
  (POST) issued by the frontend script must explicitly bundle a secure CSRF validation token. The script 
  extracts this token directly from active browser document cookies, blocking cross-site request forgery 
  attacks. Furthermore, views utilize the redirect_authenticated_user=True option, preventing logged-in users 
  from accessing basic signup portals.

 Cascading Deletion Frameworks and Relational Protection
  To prevent database errors from orphan entries, the data schema implements strict relational protection 
  rules (on_delete=models.CASCADE). When an account is terminated via the secure profile deletion pipeline, 
  the database automatically triggers a clean cascading purge. It erases all connected income logs, envelope 
  configurations, and transactional histories from disk, ensuring user privacy and data security.