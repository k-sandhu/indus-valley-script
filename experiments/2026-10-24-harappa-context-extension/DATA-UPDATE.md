# Data update proposal

Add the nine source-qualified context records in context-records-v1.json as a separate assertion layer. Use CISI identity plus source ID and page as the assertion key. Preserve H-1657 = H99-4064/8796-1 and H-2588 = H98-3493/8314-1 as explicit author joins. Retain the literal item zero padding in the source evidence. H-2587 has no normalized lot until H96/7158-01 versus H96/7458-0001 is resolved.

Keep deposit period, dating basis, manufacture date and direct sample link as separate fields. H-2588 and H-1537 have stylistic 3C assignments from mixed deposits. H-1689 has an uncertain 3A/3B boundary. H-1688, H-1682 and H-1692 are early context candidates requiring field-level qualification. No new object, global completeness gain or eligible confirmation cohort is claimed. The source manifest records the held PDF and local-only extraction on D:; no third-party source payload belongs in Git.

Integration interface: read the records array; append assertions, preserving conflict and later_cohort_disposition. Do not overwrite a corpus period with these source labels automatically. Link the original source and exact PDF page, whose namespace is the author manuscript. The site-wide chronological table is background calibration, not an individual radiocarbon measurement.
