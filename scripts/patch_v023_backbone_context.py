from pathlib import Path

paper = Path("paper/study0_v0.2.3.tex")
text = paper.read_text(encoding="utf-8")

anchor = """This design isolates the post-extractor compression intervention. It deliberately does not\nask whether a different face backbone, end-to-end compact network, nonlinear head or\nquantized representation would perform better.\n\n"""
insert = r"""\subsection{Why the ImageNet ResNet-18 starting point is pedagogical, not a face-recognition baseline}\label{sec:backbone-provenance}

The starting architecture was inherited deliberately from the public educational implementation
that motivated this work. In that implementation, a torchvision ResNet-18 initialized with
ImageNet classification weights is used as the shared backbone; every ResNet parameter is
frozen, and only the final 512-to-128 embedding head is trainable. The present repository
independently reproduces that experimental idea rather than copying its source code. Thus it
would be inaccurate to say that the face-recognition model itself was ``trained with ResNet''
on LFW. The ResNet-18 had already been trained for ImageNet object classification; LFW pair
supervision trained only the small projection placed on top of its 512D penultimate features.

This is a useful pedagogical construction because it isolates metric learning: the source
representation is fixed, so any difference among raw, random, PCA and Siamese routes is due
to the post-extractor transformation. It is not, however, a strong way to establish face
verification performance. ImageNet supervision rewards separation of object categories, not
identity discrimination among faces under changes of age, pose, illumination, expression,
occlusion and capture quality. A frozen linear head can reweight and rotate information that
already exists in the 512D source vector, but it cannot recover identity information that the
ImageNet extractor never encoded reliably. The preprocessing is likewise generic ImageNet
resize/normalization applied to LFW-deepfunneled imagery; the experiment does not evaluate a
modern face-detection/alignment/quality pipeline as part of the source representation.

The roughly ``70 percent accuracy'' recollection is therefore directionally consistent with
the replay, but it should not be used as the scientific endpoint. If a decision threshold is
chosen directly on TEST to maximize classification accuracy, the immutable Study 0 scores give
71.5\% for raw 512D and 73.0--74.7\% across the five Siamese seeds (PCA is 74.1--74.3\%). These
are descriptive, TEST-tuned values. They are optimistic for deployment because the threshold
was selected with TEST labels, and they do not replace the predeclared low-FMR non-inferiority
endpoint used in this paper. Their main value here is diagnostic: absolute face-verification
performance is weak enough that the suitability of the source backbone must be questioned
before attributing a failure to compression itself.

Modern face-recognition systems instead learn identity-discriminative embeddings with
face-specific objectives and data. Representative families include FaceNet-style metric
learning~\cite{facenet2015} and angular-margin classification such as ArcFace~\cite{arcface2019};
quality-aware variants such as AdaFace~\cite{adaface2022} further adapt the learning objective
to image quality. The next experiment therefore changes the source representation before
asking the compression question again.

"""
if "sec:backbone-provenance" not in text:
    if anchor not in text:
        raise RuntimeError("paper backbone insertion anchor not found")
    text = text.replace(anchor, anchor + insert, 1)

old = r"""The screening stage will use a dedicated SCREEN dataset that is separate from the untouched
qualification TEST set. Raw, random, PCA and Siamese routes remain matched. Screening seeds
are fixed as $\{11,29\}$ only to control exploratory cost; they cannot be used later to drop
unfavorable qualification seeds. Before screening outcomes are opened, a numerical
promotion/stop rule must be frozen. The first question is whether the raw face-specific
backbone itself is credible at the target low-FMR operating region. The second is whether at
least one 128D route shows enough retention signal relative to raw and matched controls to
justify qualification.
"""
new = old + r"""
\subsection{Backbone and dataset roles for the next experiment}

The preferred design is to use a \emph{pretrained, frozen face-specific extractor} rather
than to make backbone training part of the primary compression experiment. The exact model
must be frozen before screening with architecture, preprocessing, weight digest, training
corpus, licence and training provenance recorded. An ArcFace-family iResNet is a natural
primary candidate because its objective is explicitly identity-discriminative; AdaFace is a
reasonable secondary candidate if the programme later asks whether quality-aware source
features change the compression result. The study should not compare many backbones at once
unless that comparison is itself preregistered, because otherwise backbone choice becomes a
new post-hoc degree of freedom.

Dataset roles must also be separated. A practical public-data hierarchy is:
\begin{itemize}
\item \textbf{Projection development (TRAIN/VALIDATION):} a sufficiently large, authorized
      face-development corpus with many identities and captures, disjoint from qualification
      identities. VGGFace2~\cite{vggface2_2018} is scientifically attractive because it was
      constructed with substantial pose and age variation and has identity-separated train/test
      partitions, but its original Oxford download is no longer available; therefore it cannot
      be assumed as an automatically reproducible dependency. If it is not legitimately
      available, an alternative authorized development corpus must satisfy the same role and
      provenance requirements.
\item \textbf{Exploratory SCREEN:} conventional face-verification benchmarks such as LFW,
      CFP-FP, AgeDB-30, CALFW and CPLFW are useful as fast sanity and stress checks for
      frontal/profile, age and pose behavior. They are screening evidence only. Published
      work has documented identity overlap between common web-scale face-training corpora and
      LFW-family benchmarks~\cite{overlap2024}, so overlap must be audited rather than assumed absent.
\item \textbf{Qualification TEST:} IJB-C~\cite{ijbc2018} 1:1 template verification is a
      stronger public candidate because it contains substantially more unconstrained imagery
      and millions of impostor template comparisons, allowing evaluation at lower false-accept
      regions than LFW. It still requires an identity-overlap audit against the frozen
      backbone's training data. If disjointness or lawful access cannot be established, the
      result must be downgraded to an external benchmark rather than called qualification evidence.
\item \textbf{Operational/external validity:} no public celebrity benchmark establishes
      representativity for a passport, border, mobile or national-gallery deployment. A later
      study must therefore use authorized, population- and capture-relevant data if an
      operational claim is sought. Demographic and capture-regime stress datasets belong to
      that later external-validity stage rather than being silently folded into Study 1.
\end{itemize}

A particularly important guard follows from this hierarchy: the data used to train the face
backbone, the data used to fit the 512-to-128 projection, the exploratory screening benchmarks
and the claim-bearing qualification set are four different roles. Sharing identities across
those roles can create optimistic evidence even when file-level train/test splits are technically different.
"""
if "Backbone and dataset roles for the next experiment" not in text:
    if old not in text:
        raise RuntimeError("paper next-study insertion anchor not found")
    text = text.replace(old, new, 1)

old_threat = """\\textbf{Backbone validity.} ImageNet ResNet-18 is not designed as a face-recognition\nembedding. Poor absolute error rates are therefore unsurprising and limit transfer to real\nface systems.\n"""
new_threat = """\\textbf{Backbone validity.} ImageNet ResNet-18 is trained for generic object\nclassification, not face identity discrimination, and it is completely frozen in this\nexperiment. Only the 512-to-128 projection learns from face pairs. Poor absolute error rates\nare therefore unsurprising and limit transfer to real face systems; a linear projection\ncannot manufacture identity information absent from the frozen source embedding.\n"""
if old_threat in text:
    text = text.replace(old_threat, new_threat, 1)

ref_anchor = r"\bibitem{lfw2007}"
refs = r"""\bibitem{adaface2022}
M. Kim, A. K. Jain, and X. Liu.
AdaFace: Quality Adaptive Margin for Face Recognition.
\emph{Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition}, 2022.

\bibitem{vggface2_2018}
Q. Cao, L. Shen, W. Xie, O. M. Parkhi, and A. Zisserman.
VGGFace2: A Dataset for Recognising Faces across Pose and Age.
\emph{IEEE International Conference on Automatic Face \& Gesture Recognition}, 2018.

\bibitem{ijbc2018}
B. Maze et al.
IARPA Janus Benchmark--C: Face Dataset and Protocol.
\emph{International Conference on Biometrics}, 2018.

\bibitem{overlap2024}
H. Wu, S. Tian, J. Gutierrez, A. Bhatta, K. Ozturk, and K. W. Bowyer.
Identity Overlap Between Face Recognition Train/Test Data: Causing Optimistic Bias in Accuracy Measurement.
\emph{arXiv:2405.09403}, 2024.

"""
if "\\bibitem{adaface2022}" not in text:
    if ref_anchor not in text:
        raise RuntimeError("paper bibliography insertion anchor not found")
    text = text.replace(ref_anchor, refs + ref_anchor, 1)

paper.write_text(text, encoding="utf-8")

report = Path("STUDY0_FINAL_REPORT.md")
r = report.read_text(encoding="utf-8")
anchor_r = "The experiment is intentionally exploratory. ImageNet ResNet-18 is not a face-recognition backbone, and LFW DevTest has only 500 impostor pairs, so it cannot establish industrial very-low-FMR claims.\n\n"
insert_r = """### Why the ResNet-18 starting point matters

The original public implementation that motivated this work used a **torchvision ResNet-18 pretrained on ImageNet and then fully frozen**. Only the final 512→128 linear embedding head was trained from LFW pairs. So it is more precise to say that Study 0 trained a **small Siamese projection on top of generic ImageNet features**, not that a ResNet-18 face recognizer was trained on LFW.

That distinction explains much of the weak absolute performance. ImageNet training optimizes generic object-category discrimination, not identity separation between faces under age, pose, illumination, expression, occlusion and capture-quality changes. A linear head can reorganize information already present in the 512D vector, but it cannot recreate identity information that the frozen source representation did not preserve.

The remembered “~70% accuracy” is consistent with the immutable replay, but it is not the scientific endpoint. If a threshold is optimized directly on TEST, descriptive accuracy is **71.5% for raw 512D** and **73.0–74.7% across Siamese seeds** (PCA: **74.1–74.3%**). These values are TEST-tuned and therefore non-deployable. They are useful mainly as a sanity check showing that the source representation itself is weak for face verification.

A stronger continuation should therefore start from a **pretrained face-specific embedding** (for example an ArcFace-family model with pinned weights and training provenance), keep that backbone frozen, and then ask the compression question again.

"""
if "Why the ResNet-18 starting point matters" not in r:
    if anchor_r not in r:
        raise RuntimeError("report backbone insertion anchor not found")
    r = r.replace(anchor_r, anchor_r + insert_r, 1)

next_old = "The next experiment will replace ImageNet ResNet-18 with a face-specific backbone. Its current design uses a non-claim-bearing screening stage before qualification:\n"
next_new = """The next experiment will replace ImageNet ResNet-18 with a face-specific backbone. Dataset roles should be explicit:

- **TRAIN / VALIDATION for the projection:** a sufficiently large authorized face-development corpus, identity-disjoint from qualification data. VGGFace2 is scientifically attractive for pose/age diversity, but its original Oxford download is no longer available, so access and licence cannot be assumed.
- **SCREEN:** LFW, CFP-FP, AgeDB-30, CALFW and CPLFW can provide fast, non-claim-bearing sanity/stress checks; identity overlap with the backbone's training corpus must be audited.
- **Qualification TEST:** IJB-C 1:1 template verification is the preferred public candidate because it supports a substantially richer unconstrained protocol and far more impostor comparisons than LFW. It still requires training/test identity-overlap and lawful-access checks.
- **Operational validity:** a later study needs authorized data representative of the actual population, sensor and capture process; public celebrity benchmarks do not establish that claim.

Its current design uses a non-claim-bearing screening stage before qualification:
"""
if next_old in r:
    r = r.replace(next_old, next_new, 1)
report.write_text(r, encoding="utf-8")
