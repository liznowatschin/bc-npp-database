Data Standards
==============

Evidence levels
---------------

.. list-table::
   :header-rows: 1

   * - Level
     - Meaning
   * - A
     - Peer-reviewed literature or government publication.
   * - B
     - University, botanical garden, herbarium, or recognized conservation
       organization.
   * - C
     - Reputable horticultural reference or native plant nursery.
   * - D
     - Expert consensus or provisional interpretation where stronger sources
       are not available.
   * - Mixed
     - Multiple evidence levels support different fields in the record.

Unknown values
--------------

Use ``Unknown`` where a field is relevant but not yet verified. Leave a field
blank only where it is not applicable or intentionally not populated.

Taxonomy
--------

Use current accepted botanical names as the primary value. Record synonyms where
important for searchability and legacy references.

Height threshold
----------------

Version 1.0.0 prioritizes species with mature height <= 60 cm, or species that
can be reasonably maintained below that threshold in urban contexts.

Scoring
-------

Scores must not hide evidence uncertainty. Keep source confidence and ecological
score as separate values.
