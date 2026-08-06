# GitHub

Eu daria o nome **`grad-radar`**.

É curto, fácil de lembrar, funciona bem em inglês americano e não prende o sistema apenas à UFSCar, USP, São Carlos ou IA. O escopo inicial pode ser local, mas o projeto continua preparado para crescer.

Também evitaria `postgrad` no nome. Em inglês americano, **graduate programs**, **graduate school** e **grad programs** soam mais naturais para mestrado e doutorado.

Repository name: `grad-radar`

Product name: `GradRadar`

Tagline:
`Discover, compare, and track graduate opportunities.`

GitHub description:
`A self-hosted system for discovering, comparing, and tracking tuition-free, in-person graduate programs, admissions calls, research groups, faculty, scholarships, and application deadlines.`

Initial scope:
`Computer Science, Artificial Intelligence, Machine Learning, NLP, LLMs, and related graduate opportunities at UFSCar and USP São Carlos.`

Suggested GitHub topics:

`graduate-school`
`graduate-programs`
`academic-opportunities`
`admissions`
`research`
`computer-science`
`artificial-intelligence`
`machine-learning`
`llm`
`ufscar`
`usp`
`sao-carlos`
`self-hosted`

O nome comunica exatamente a proposta: não é apenas uma lista de cursos, mas um radar que monitora programas, editais, prazos, docentes, laboratórios e oportunidades.

Um README inicial poderia seguir esta estrutura:

## GradRadar

> Discover, compare, and track graduate opportunities.

GradRadar is a self-hosted system for discovering, organizing, comparing, and tracking graduate programs and academic opportunities.

The project is initially focused on tuition-free, in-person graduate programs in Computer Science, Artificial Intelligence, Machine Learning, Natural Language Processing, Large Language Models, Software Engineering, and related fields in São Carlos, Brazil.

The initial institutions include UFSCar and USP São Carlos, especially programs connected to the UFSCar Department of Computing and the USP Institute of Mathematics and Computer Sciences.

## Motivation

Information about graduate programs is usually fragmented across institutional websites, admissions notices, PDF documents, faculty pages, research group websites, academic calendars, and application systems.

This fragmentation makes it difficult to answer practical questions such as:

* Which programs are currently accepting applications?
* When will the next admissions notice be published?
* Is the program tuition-free and in person?
* Which research areas are related to AI, NLP, LLMs, or Software Engineering?
* Which faculty members are accepting new students?
* Which laboratories and research groups are relevant?
* Are class schedules compatible with a full-time job?
* Which documents are required?
* Is special student enrollment available?
* Are scholarships available?
* Which opportunities best match each candidate's academic and professional goals?

GradRadar aims to centralize this information and turn it into a structured decision-making system.

## Initial scope

The first version will focus on:

* UFSCar graduate programs related to Computer Science;
* UFSCar Computer Science Graduate Program;
* USP São Carlos graduate programs;
* ICMC-USP Computer Science and Computational Mathematics Graduate Program;
* regular graduate admissions;
* special student admissions;
* master's degree opportunities;
* research groups and laboratories;
* faculty and potential advisors;
* application deadlines and required documents.

The first tracked areas will include:

* Artificial Intelligence;
* Machine Learning;
* Natural Language Processing;
* Large Language Models;
* Information Retrieval;
* Data Science;
* Software Engineering;
* Distributed Systems;
* Databases;
* Human-Computer Interaction;
* Computer Vision.

## Core features

### Graduate program catalog

Store and organize:

* institution;
* campus;
* department;
* program name;
* degree level;
* academic or professional track;
* delivery format;
* estimated duration;
* tuition information;
* official website;
* current admissions status.

### Admissions monitoring

Track:

* admissions notices;
* calls for applications;
* application opening and closing dates;
* number of available positions;
* selection stages;
* required documents;
* entrance examinations;
* interviews;
* research proposals;
* English proficiency requirements;
* advisor contact requirements;
* results and waitlists.

### Faculty and research groups

Map:

* faculty members;
* potential advisors;
* research interests;
* institutional profiles;
* Lattes CVs;
* ORCID profiles;
* laboratories;
* research groups;
* current projects;
* recent publications.

The main analysis structure will be:

`institution → program → research area → faculty member → laboratory → project → course`

### Courses and schedules

Track:

* course name;
* instructor;
* syllabus;
* credits;
* workload;
* weekday;
* start and end time;
* campus;
* attendance requirements;
* assessment format;
* compatibility with full-time employment.

### Scholarships and costs

Store information about:

* tuition;
* application fees;
* transportation;
* meals;
* academic materials;
* CAPES scholarships;
* CNPq scholarships;
* FAPESP scholarships;
* institutional funding;
* employment restrictions;
* exclusive dedication requirements.

### Candidate profiles

GradRadar should support multiple candidates, initially Victor and João.

Each candidate should have an independent profile containing:

* areas of interest;
* preferred institutions;
* preferred research topics;
* schedule constraints;
* document checklist;
* application history;
* saved programs;
* opportunity scores;
* personal notes.

### Application pipeline

Each opportunity may use the following workflow:

`discovered → saved → reviewing → eligible → waiting for notice → preparing documents → contacting advisor → applied → examination → interview → accepted → waitlisted → rejected → enrolled → discarded`

### Opportunity scoring

Programs and admissions opportunities may be ranked according to:

* relevance to AI and LLMs;
* research area compatibility;
* faculty interest;
* laboratory quality;
* schedule compatibility;
* in-person availability;
* tuition-free status;
* scholarship availability;
* distance;
* networking potential;
* professional impact;
* feasibility while working full time.

## Automated monitoring

Future versions should monitor official institutional sources.

The monitoring pipeline may:

1. access registered official sources;
2. detect new admissions notices;
3. identify page and PDF changes;
4. extract dates and requirements;
5. compare document versions;
6. preserve the original source;
7. record the last verification timestamp;
8. generate deadline and update notifications.

Official sources should always take precedence over third-party aggregators.

## Development principles

* Official sources first;
* traceable and verifiable information;
* manual-first MVP;
* automation after domain validation;
* self-hosted whenever practical;
* multiple candidate support;
* English-first codebase and documentation;
* modular architecture;
* reproducible development environments;
* declarative infrastructure where applicable.

## Proposed stack

* Next.js;
* TypeScript;
* FastAPI;
* Python;
* PostgreSQL or Supabase;
* scheduled background jobs;
* Beautiful Soup or Playwright;
* PDF extraction tools;
* email, Telegram, Discord, or push notifications;
* Nix and NixOS for reproducible environments and deployment.

The final architecture will be defined during implementation.

## MVP

The first release should include:

1. manual graduate program registration;
2. admissions notice registration;
3. application deadline calendar;
4. faculty and research area catalog;
5. filters by institution, research area, format, and tuition;
6. candidate profiles;
7. document checklists;
8. application pipelines;
9. opportunity scoring;
10. official source links.

Automated scraping and document monitoring should be introduced only after the manual workflow and data model are validated.

## Project status

Planning and requirements definition.

## License

License to be defined.

Algumas alternativas viáveis seriam:

* `gradscope`: mais “produto”, mas menos autoexplicativo;
* `gradwatch`: enfatiza monitoramento;
* `academic-radar`: permite cobrir eventos, bolsas e outras oportunidades, mas fica genérico;
* `sanca-grad-radar`: comunica São Carlos, porém restringe a expansão;
* `graduate-opportunity-tracker`: extremamente descritivo, mas longo.

Entre elas, **GradRadar / `grad-radar`** tem o melhor equilíbrio entre clareza, identidade e possibilidade de expansão.
