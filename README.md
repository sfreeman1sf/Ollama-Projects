# Synthetic Nervous System (SNS)
### Training BERT to Detect Emotional Manipulation and Adversarial Behavior in AI Systems

![Confusion Matrix](sns_bert_confusion_matrix.png)

> *"Current AI lacks the ability to recognize manipulative behavior the way a human empath would. This project bridges the siloed domains of psychology and cybersecurity to build an emotional safety layer for Large Language Models."*

---

## Overview

The Synthetic Nervous System is a multimodal adversarial detection framework that gives AI the pattern recognition instincts of a human empath. It operates on a core insight: **inconsistency is a safety signal.** The same psychological patterns that human empaths use to detect manipulation — gaslighting, blame-shifting, trust violations — map directly onto both conversational text and network traffic anomalies.

This project is a Master's Capstone in AI/ML combining three disciplines that rarely talk to each other:

- **Psychology & NLP** — detecting emotional manipulation in conversational text
- **Cybersecurity** — detecting adversarial behavior in network traffic
- **Applied Machine Learning** — fusing both signals into a single detection framework

---

## Results

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|----|
| BERT (conversational) | **96%** | 0.97 | 0.96 | 0.96 |
| Random Forest (network) | *in progress* | — | — | — |
| Fusion (multimodal) | *in progress* | — | — | — |

BERT was fine-tuned on 200 labeled conversations across 6 manipulation pattern categories and evaluated on 28 completely unseen conversations.

---

## The Six-Vector Manipulation Taxonomy

The dataset labels conversations across six adversarial pattern types — three psychological and three technical:

| Vector | Type | Description |
|--------|------|-------------|
| `emotional_invalidation` | Psychological | Dismissing or denying another's emotional experience |
| `gaslighting` | Psychological | Making someone doubt their own perception or memory |
| `blame_shifting` | Psychological | Redirecting responsibility for harm onto the victim |
| `goalpost_moving` | Technical | Continuously shifting parameters to confuse the model |
| `trust_violation` | Technical | Exploiting previously established warm context |
| `adversarial_prompting` | Technical | Overt jailbreak attempts disguised as legitimate queries |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Synthetic Nervous System                │
│                                                     │
│  NLP Layer              Network Layer               │
│  ──────────             ──────────────              │
│  BERT fine-tuned   +    Random Forest               │
│  (conversational        (traffic features)          │
│   manipulation)                                     │
│        │                      │                     │
│        └──────────┬───────────┘                     │
│                   ▼                                 │
│           Fusion Classifier                         │
│         (compound threat signal)                    │
└─────────────────────────────────────────────────────┘
```

The two datasets are linked by a shared `session_id` key, allowing the system to correlate suspicious language with suspicious network behavior for the same interaction — a compound signal that transcends the limitations of either detector alone.

---

## Dataset

Two synthetic datasets, linked by `session_id`:

**`sns_bert.db`** — Conversational manipulation dataset
- 200 realistic text conversations (100 safe / 100 unsafe)
- Labeled across 6 pattern types with severity scores (0–3)
- Pre-split into train (140) / validation (32) / test (28)
- Tables: `conversations`, `labeled_data`, `users`, `threat_log`, `model_predictions`, `training_splits`, `pattern_taxonomy`

**`sns_network.db`** — Network traffic dataset
- 200 sessions (100 normal / 100 suspicious)
- 38,028 correlated packet events
- 6 attack pattern types mapped to NLP taxonomy analogs
- Pre-computed ML features in `traffic_features` table
- Tables: `network_sessions`, `packet_events`, `traffic_features`, `traffic_taxonomy`

> The `.db` files are not included in this repo due to size. Run the builder scripts to generate them locally.

---

## Network Traffic ↔ NLP Taxonomy Mapping

| Psychological Pattern | Network Equivalent | Key Signal |
|----------------------|-------------------|------------|
| Gaslighting | C2 Beaconing | beacon_regularity > 0.85 |
| Adversarial Prompting | Port Scanning | sequential_port_flag = 1 |
| Trust Violation | Data Exfiltration | large_outbound_flag = 1 |
| Trust Violation | Session Hijacking | ip_changed = 1 |

---

## Project Structure

```
synthetic-nervous-system/
│
├── The Brains (Python scripts)/
│   ├── sns_bert_db.py          # Builds conversational dataset + SQLite DB
│   ├── sns_network_traffic.py  # Builds network traffic dataset + SQLite DB
│   ├── SNS_BERT_Training.ipynb # BERT fine-tuning notebook (runs on Google Colab)
│   ├── sns_rf_train.py         # Random Forest on network features (coming)
│   └── sns_fusion_eval.py      # Multimodal fusion evaluation (coming)
│
├── The Documentation/
│   ├── The_Synthetic_Nervous_System_2.pdf  # Visual research deck
│   └── capstone_project.docx               # Project narrative
│
└── sns_bert_confusion_matrix.png           # Test set results
```

---

## How to Run

**Step 1 — Generate the databases locally:**
```bash
pip install sqlite3
python "The Brains (Python scripts)/sns_bert_db.py"
python "The Brains (Python scripts)/sns_network_traffic.py"
```

**Step 2 — Train BERT (requires GPU — use Google Colab free tier):**
1. Upload `sns_bert.db` and `sns_network.db` to Google Drive
2. Open `SNS_BERT_Training.ipynb` in Google Colab
3. Set Runtime → T4 GPU
4. Run all cells

**Requirements:**
```
transformers
torch
scikit-learn
pandas
numpy
seaborn
matplotlib
```

---

## The Biological Premise

Human empathy is fundamentally a neurological survival mechanism. It relies on evaluating consistency over time to determine safety. The empathic instinct tracks data points: the more consistent a communicator's patterns, the higher the trust. When linguistic patterns shift through emotional invalidation or gaslighting, the biological nervous system recognizes a safety signal.

This project translates that sequence-based self-preservation instinct into a synthetic framework for artificial intelligence — giving AI the ability to recognize manipulative behavior the way a human empath would.

---

## Stack

`Python` `PyTorch` `HuggingFace Transformers` `BERT` `scikit-learn` `SQLite` `pandas` `numpy` `Google Colab` `Tesla T4 GPU`

---

## Author

**Stacey Freeman**
Master's Candidate — Artificial Intelligence & Machine Learning
GitHub: [@sfreeman1sf](https://github.com/sfreeman1sf)

---

## Status

- [x] Conversational dataset built (200 conversations, 6 pattern types)
- [x] Network traffic dataset built (200 sessions, 38,028 packets)
- [x] BERT fine-tuned — 96% test accuracy
- [ ] Random Forest classifier (network features)
- [ ] Multimodal fusion evaluation
- [ ] Capstone paper

---

*Master's Capstone Project — 2026*
