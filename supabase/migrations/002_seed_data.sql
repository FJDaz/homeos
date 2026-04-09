-- 002_seed_data.sql
-- Seed classes and students for AetherFlow

INSERT INTO classes (id, name, subject) VALUES
    ('dnamde3', 'DNMADE3_2026', 'OLN'),
    ('dnmade1-2026', 'DNMADE1_2026', 'OLN'),
    ('dnmade2-2026', 'DNMADE2_2026', 'OLN')
ON CONFLICT (id) DO NOTHING;

INSERT INTO students (id, class_id, display, last_name, first_name, project_id) VALUES
    -- DNMADE3
    ('darnoux-cyrielle', 'dnamde3', 'DARNOUX Cyrielle', 'DARNOUX', 'Cyrielle', 'dnamde3-darnoux-cyrielle'),
    ('delaplace-juliette', 'dnamde3', 'DELAPLACE Juliette', 'DELAPLACE', 'Juliette', 'dnamde3-delaplace-juliette'),
    ('dumont-hugo', 'dnamde3', 'DUMONT Hugo', 'DUMONT', 'Hugo', 'dnamde3-dumont-hugo'),
    ('gwazda-charline', 'dnamde3', 'GWAZDA Charline', 'GWAZDA', 'Charline', 'dnamde3-gwazda-charline'),
    ('hiver-lyse', 'dnamde3', 'HIVER Lyse', 'HIVER', 'Lyse', 'dnamde3-hiver-lyse'),
    ('le-bellego-margo', 'dnamde3', 'LE BELLEGO Margo', 'LE BELLEGO', 'Margo', 'dnamde3-le-bellego-margo'),
    ('overmeer-maelys', 'dnamde3', 'OVERMEER Maëlys', 'OVERMEER', 'Maelys', 'dnamde3-overmeer-maelys'),
    ('paulhan-ann-zoe', 'dnamde3', 'PAULHAN Ann-Zoe', 'PAULHAN', 'Ann-Zoe', 'dnamde3-paulhan-ann-zoe'),
    ('romary-celio', 'dnamde3', 'ROMARY Celio', 'ROMARY', 'Celio', 'dnamde3-romary-celio'),
    ('salle-abigael', 'dnamde3', 'SALLÉ Abigaël', 'SALLE', 'Abigael', 'dnamde3-salle-abigael'),
    ('schnering-marylou', 'dnamde3', 'SCHNERING Marylou', 'SCHNERING', 'Marylou', 'dnamde3-schnering-marylou'),
    ('serre-lilou', 'dnamde3', 'SERRE Lilou', 'SERRE', 'Lilou', 'dnamde3-serre-lilou'),
    -- DNMADE1
    ('blart-samuel', 'dnmade1-2026', 'BLART Samuel', 'BLART', 'Samuel', 'dnmade1-2026-blart-samuel'),
    ('blin-zoe', 'dnmade1-2026', 'BLIN Zoé', 'BLIN', 'Zoe', 'dnmade1-2026-blin-zoe'),
    ('calais-jeanne', 'dnmade1-2026', 'CALAIS Jeanne', 'CALAIS', 'Jeanne', 'dnmade1-2026-calais-jeanne'),
    ('chareyron--gamain-lou-ann', 'dnmade1-2026', 'CHAREYRON--GAMAIN Lou-Ann', 'CHAREYRON--GAMAIN', 'Lou-Ann', 'dnmade1-2026-chareyron--gamain-lou-ann'),
    ('desseaux-nael', 'dnmade1-2026', 'DESSEAUX Naël', 'DESSEAUX', 'Nael', 'dnmade1-2026-desseaux-nael'),
    ('drelon-oceane', 'dnmade1-2026', 'DRELON Océane', 'DRELON', 'Oceane', 'dnmade1-2026-drelon-oceane'),
    ('ezzyani-sabrine', 'dnmade1-2026', 'EZZYANI Sabrine', 'EZZYANI', 'Sabrine', 'dnmade1-2026-ezzyani-sabrine'),
    ('fadier-aya', 'dnmade1-2026', 'FADIER Aya', 'FADIER', 'Aya', 'dnmade1-2026-fadier-aya'),
    ('hassaini-riad', 'dnmade1-2026', 'HASSAINI Riad', 'HASSAINI', 'Riad', 'dnmade1-2026-hassaini-riad'),
    ('hurdebourg-noe', 'dnmade1-2026', 'HURDEBOURG Noé', 'HURDEBOURG', 'Noe', 'dnmade1-2026-hurdebourg-noe'),
    ('lautard-victor', 'dnmade1-2026', 'LAUTARD Victor', 'LAUTARD', 'Victor', 'dnmade1-2026-lautard-victor'),
    ('le-strat-louane', 'dnmade1-2026', 'LE STRAT Louane', 'LE STRAT', 'Louane', 'dnmade1-2026-le-strat-louane'),
    ('moreau-julie', 'dnmade1-2026', 'MOREAU Julie', 'MOREAU', 'Julie', 'dnmade1-2026-moreau-julie'),
    ('prodhomme-arthur', 'dnmade1-2026', 'PRODHOMME Arthur', 'PRODHOMME', 'Arthur', 'dnmade1-2026-prodhomme-arthur'),
    ('rossi-solene', 'dnmade1-2026', 'ROSSI Solène', 'ROSSI', 'Solene', 'dnmade1-2026-rossi-solene'),
    ('rossi-valentine', 'dnmade1-2026', 'ROSSI Valentine', 'ROSSI', 'Valentine', 'dnmade1-2026-rossi-valentine'),
    ('volant--huguet-sandy', 'dnmade1-2026', 'VOLANT--HUGUET Sandy', 'VOLANT--HUGUET', 'Sandy', 'dnmade1-2026-volant--huguet-sandy'),
    ('warambourg-maia', 'dnmade1-2026', 'WARAMBOURG Maïa', 'WARAMBOURG', 'Maia', 'dnmade1-2026-warambourg-maia'),
    -- DNMADE2
    ('absolu-alice', 'dnmade2-2026', 'ABSOLU Alice', 'ABSOLU', 'Alice', 'dnmade2-2026-absolu-alice'),
    ('cazaux-guyon-loula', 'dnmade2-2026', 'CAZAUX-GUYON Loula', 'CAZAUX-GUYON', 'Loula', 'dnmade2-2026-cazaux-guyon-loula'),
    ('dodier-zoe', 'dnmade2-2026', 'DODIER Zoé', 'DODIER', 'Zoe', 'dnmade2-2026-dodier-zoe'),
    ('dulhoste-emma', 'dnmade2-2026', 'DULHOSTE Emma', 'DULHOSTE', 'Emma', 'dnmade2-2026-dulhoste-emma'),
    ('hay-lya', 'dnmade2-2026', 'HAY Lya', 'HAY', 'Lya', 'dnmade2-2026-hay-lya'),
    ('hervieux-domitille', 'dnmade2-2026', 'HERVIEUX Domitille', 'HERVIEUX', 'Domitille', 'dnmade2-2026-hervieux-domitille'),
    ('marie-eleonore', 'dnmade2-2026', 'MARIE Eléonore', 'MARIE', 'Eleonore', 'dnmade2-2026-marie-eleonore'),
    ('mkadara-nasma', 'dnmade2-2026', 'MKADARA Nasma', 'MKADARA', 'Nasma', 'dnmade2-2026-mkadara-nasma'),
    ('pouillot-alix', 'dnmade2-2026', 'POUILLOT Alix', 'POUILLOT', 'Alix', 'dnmade2-2026-pouillot-alix'),
    ('sauvage-chloe', 'dnmade2-2026', 'SAUVAGE Chloé', 'SAUVAGE', 'Chloe', 'dnmade2-2026-sauvage-chloe'),
    ('viard-sixtine', 'dnmade2-2026', 'VIARD Sixtine', 'VIARD', 'Sixtine', 'dnmade2-2026-viard-sixtine'),
    ('wehrle-evan', 'dnmade2-2026', 'WEHRLE Evan', 'WEHRLE', 'Evan', 'dnmade2-2026-wehrle-evan'),
    ('zaffiroff-adeline', 'dnmade2-2026', 'ZAFFIROFF Adeline', 'ZAFFIROFF', 'Adeline', 'dnmade2-2026-zaffiroff-adeline')
ON CONFLICT (id, class_id) DO NOTHING;

INSERT INTO projects (id, name, path, user_id) VALUES
    ('dnamde3-darnoux-cyrielle', 'DARNOUX Cyrielle', 'projects/dnamde3-darnoux-cyrielle', 'darnoux-cyrielle'),
    ('dnamde3-delaplace-juliette', 'DELAPLACE Juliette', 'projects/dnamde3-delaplace-juliette', 'delaplace-juliette'),
    ('dnamde3-dumont-hugo', 'DUMONT Hugo', 'projects/dnamde3-dumont-hugo', 'dumont-hugo'),
    ('dnamde3-gwazda-charline', 'GWAZDA Charline', 'projects/dnamde3-gwazda-charline', 'gwazda-charline'),
    ('dnamde3-hiver-lyse', 'HIVER Lyse', 'projects/dnamde3-hiver-lyse', 'hiver-lyse'),
    ('dnamde3-le-bellego-margo', 'LE BELLEGO Margo', 'projects/dnamde3-le-bellego-margo', 'le-bellego-margo'),
    ('dnamde3-overmeer-maelys', 'OVERMEER Maëlys', 'projects/dnamde3-overmeer-maelys', 'overmeer-maelys'),
    ('dnamde3-paulhan-ann-zoe', 'PAULHAN Ann-Zoe', 'projects/dnamde3-paulhan-ann-zoe', 'paulhan-ann-zoe'),
    ('dnamde3-romary-celio', 'ROMARY Celio', 'projects/dnamde3-romary-celio', 'romary-celio'),
    ('dnamde3-salle-abigael', 'SALLÉ Abigaël', 'projects/dnamde3-salle-abigael', 'salle-abigael'),
    ('dnamde3-schnering-marylou', 'SCHNERING Marylou', 'projects/dnamde3-schnering-marylou', 'schnering-marylou'),
    ('dnamde3-serre-lilou', 'SERRE Lilou', 'projects/dnamde3-serre-lilou', 'serre-lilou')
ON CONFLICT (id) DO NOTHING;
