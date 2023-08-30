To add tags to existing project schema
*replace "Project-1"
```sql
create table if not exists "Project-1".models_prompts_tags
(
    id    serial
        primary key,
    tag   varchar(250) not null
        unique,
    color varchar(15)
);

alter table "Project-1".models_prompts_tags
    owner to carrier;



create table "Project-1".models_prompts_tags_association
(
    id        serial
        primary key,
    prompt_id integer
        references "Project-1".models_prompts,
    tag_id    integer
        references "Project-1".models_prompts_tags
);

alter table "Project-1".models_prompts_tags_association
    owner to carrier;
```