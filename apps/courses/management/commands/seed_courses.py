from django.core.management.base import BaseCommand
from apps.courses.models import Department, Course, CourseModule, CourseActivity


DEPARTMENTS = [
    {"name": "Computer Science", "code": "CS"},
    {"name": "Mathematics", "code": "MATH"},
    {"name": "Data Science", "code": "DS"},
    {"name": "Electrical Engineering", "code": "EE"},
    {"name": "Statistics", "code": "STAT"},
    {"name": "Business & Management", "code": "BUS"},
    {"name": "Psychology", "code": "PSY"},
    {"name": "Physics", "code": "PHY"},
]

COURSES = [
    # ── Computer Science ────────────────────────────────────────────
    {
        "code": "CS101",
        "title": "Introduction to Programming",
        "description": "Foundational programming concepts using Python. Covers variables, control flow, functions, and basic data structures.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "tags": ["python", "programming", "beginner", "algorithms", "problem solving"],
        "syllabus_text": "Introduction to computational thinking. Variables and data types. Control flow: conditionals and loops. Functions and scope. Lists, dictionaries, and tuples. File I/O. Basic debugging and testing. Introduction to object-oriented programming.",
    },
    {
        "code": "CS102",
        "title": "Data Structures and Algorithms",
        "description": "Study of fundamental data structures and algorithm design techniques including complexity analysis.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS101"],
        "tags": ["algorithms", "data structures", "complexity", "sorting", "trees", "graphs"],
        "syllabus_text": "Algorithm analysis and Big-O notation. Arrays and linked lists. Stacks, queues, and deques. Hash tables. Binary trees and BSTs. Heaps and priority queues. Graph representations and traversals. Sorting algorithms: merge sort, quicksort, heapsort. Dynamic programming basics.",
    },
    {
        "code": "CS201",
        "title": "Object-Oriented Programming",
        "description": "Deep dive into OOP principles: encapsulation, inheritance, polymorphism, and design patterns.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS101"],
        "tags": ["oop", "design patterns", "java", "python", "software engineering"],
        "syllabus_text": "Classes and objects. Encapsulation and access modifiers. Inheritance and method overriding. Polymorphism and interfaces. Abstract classes. Design patterns: Singleton, Factory, Observer, Strategy. SOLID principles. Unit testing with mocks.",
    },
    {
        "code": "CS301",
        "title": "Database Systems",
        "description": "Relational database design, SQL, normalization, transactions, and introduction to NoSQL systems.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS102"],
        "tags": ["databases", "sql", "nosql", "data modeling", "transactions"],
        "syllabus_text": "Relational model and SQL. ER diagrams and schema design. Normalization: 1NF through BCNF. Joins, subqueries, and aggregations. Indexing and query optimization. Transactions and ACID properties. Concurrency control. Introduction to NoSQL: document, key-value, and graph stores.",
    },
    {
        "code": "CS302",
        "title": "Operating Systems",
        "description": "Principles of modern operating systems including process management, memory, and file systems.",
        "credits": 4,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS102"],
        "tags": ["operating systems", "concurrency", "memory management", "linux", "systems programming"],
        "syllabus_text": "Processes and threads. CPU scheduling algorithms. Synchronization: semaphores and mutexes. Deadlock detection and prevention. Virtual memory and paging. File systems and I/O. Security and protection. Case studies: Linux and Windows internals.",
    },
    {
        "code": "CS303",
        "title": "Computer Networks",
        "description": "Layered network architecture, protocols, routing, and network security fundamentals.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS102"],
        "tags": ["networking", "tcp/ip", "protocols", "security", "web"],
        "syllabus_text": "OSI and TCP/IP models. Physical and data link layers. IP addressing and subnetting. TCP and UDP protocols. DNS, HTTP, and application layer. Routing protocols: OSPF and BGP. Network security: firewalls and VPNs. Socket programming.",
    },
    {
        "code": "CS401",
        "title": "Software Engineering",
        "description": "Software development lifecycle, agile methodologies, testing strategies, and project management.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS201"],
        "tags": ["software engineering", "agile", "testing", "devops", "team collaboration"],
        "syllabus_text": "SDLC models: waterfall, agile, scrum. Requirements engineering. UML diagrams. Test-driven development. Continuous integration and deployment. Version control with Git. Code review practices. Software metrics and quality assurance. Project management tools.",
    },
    {
        "code": "CS402",
        "title": "Artificial Intelligence",
        "description": "Core AI concepts: search, knowledge representation, planning, and an introduction to machine learning.",
        "credits": 4,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS102", "MATH201"],
        "tags": ["artificial intelligence", "search algorithms", "machine learning", "knowledge representation", "planning"],
        "syllabus_text": "Intelligent agents. Uninformed and informed search: BFS, DFS, A*. Adversarial search and game playing. Constraint satisfaction. Logical reasoning and knowledge bases. Probabilistic reasoning: Bayesian networks. Introduction to machine learning. Natural language processing overview.",
    },
    {
        "code": "CS403",
        "title": "Web Development",
        "description": "Full-stack web development covering HTML, CSS, JavaScript, REST APIs, and modern frameworks.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS201"],
        "tags": ["web development", "javascript", "react", "rest api", "frontend", "backend"],
        "syllabus_text": "HTML5 and semantic markup. CSS3 and responsive design. JavaScript ES6+. DOM manipulation. Asynchronous programming: promises and async/await. React fundamentals. RESTful API design. Node.js and Express. Authentication with JWT. Deployment and hosting.",
    },
    {
        "code": "CS501",
        "title": "Machine Learning",
        "description": "Supervised, unsupervised, and reinforcement learning algorithms with practical implementation.",
        "credits": 4,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["CS402", "STAT201"],
        "tags": ["machine learning", "supervised learning", "neural networks", "scikit-learn", "python"],
        "syllabus_text": "Linear and logistic regression. Decision trees and random forests. Support vector machines. Neural networks and backpropagation. Clustering: k-means and hierarchical. Dimensionality reduction: PCA. Model evaluation and cross-validation. Ensemble methods. Regularisation techniques.",
    },
    {
        "code": "CS502",
        "title": "Deep Learning",
        "description": "Advanced neural network architectures including CNNs, RNNs, transformers, and generative models.",
        "credits": 4,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["CS501"],
        "tags": ["deep learning", "neural networks", "cnn", "rnn", "transformers", "pytorch", "tensorflow"],
        "syllabus_text": "Feedforward networks and backpropagation. Convolutional neural networks for image tasks. Recurrent neural networks and LSTMs. Attention mechanisms and transformers. Transfer learning and fine-tuning. Generative adversarial networks. Variational autoencoders. PyTorch and TensorFlow practice.",
    },
    {
        "code": "CS503",
        "title": "Natural Language Processing",
        "description": "Text processing, language models, sentiment analysis, and transformer-based NLP systems.",
        "credits": 4,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["CS501"],
        "tags": ["nlp", "text mining", "transformers", "bert", "language models", "sentiment analysis"],
        "syllabus_text": "Text preprocessing and tokenisation. Bag-of-words and TF-IDF. Word embeddings: Word2Vec and GloVe. Sequence models for NLP. BERT and pre-trained transformers. Named entity recognition. Question answering. Machine translation. Sentiment analysis. Hugging Face ecosystem.",
    },
    {
        "code": "CS504",
        "title": "Computer Vision",
        "description": "Image processing, feature extraction, object detection, and segmentation using deep learning.",
        "credits": 4,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["CS502"],
        "tags": ["computer vision", "image processing", "cnn", "object detection", "opencv"],
        "syllabus_text": "Image formation and filtering. Edge detection and feature descriptors. Convolutional networks for vision. Object detection: YOLO and Faster R-CNN. Semantic segmentation. Image generation with GANs. Video understanding. 3D vision and depth estimation. OpenCV and PyTorch.",
    },
    {
        "code": "CS505",
        "title": "Cloud Computing",
        "description": "Cloud architectures, AWS/GCP services, containerisation, and scalable distributed systems.",
        "credits": 3,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["CS302", "CS303"],
        "tags": ["cloud computing", "aws", "docker", "kubernetes", "devops", "microservices"],
        "syllabus_text": "Cloud service models: IaaS, PaaS, SaaS. AWS core services: EC2, S3, RDS, Lambda. Containerisation with Docker. Orchestration with Kubernetes. Serverless computing. Auto-scaling and load balancing. Cloud security and IAM. Cost optimisation. CI/CD pipelines.",
    },
    {
        "code": "CS506",
        "title": "Cybersecurity Fundamentals",
        "description": "Network security, cryptography, vulnerability assessment, and secure coding practices.",
        "credits": 3,
        "dept": "CS",
        "level": "undergraduate",
        "prereqs": ["CS303"],
        "tags": ["cybersecurity", "cryptography", "network security", "ethical hacking", "secure coding"],
        "syllabus_text": "Security principles: CIA triad. Symmetric and asymmetric cryptography. PKI and certificates. Network attacks and defences. Web application security: OWASP Top 10. Authentication and authorisation. Vulnerability scanning and penetration testing. Incident response. Security policies.",
    },

    # ── Mathematics ─────────────────────────────────────────────────
    {
        "code": "MATH101",
        "title": "Calculus I",
        "description": "Limits, differentiation, and integration of single-variable functions with applications.",
        "credits": 4,
        "dept": "MATH",
        "level": "undergraduate",
        "tags": ["calculus", "differentiation", "integration", "limits", "mathematics"],
        "syllabus_text": "Limits and continuity. Derivatives and differentiation rules. Chain rule and implicit differentiation. Applications: optimisation and related rates. Definite and indefinite integrals. Fundamental theorem of calculus. Substitution rule. Area between curves.",
    },
    {
        "code": "MATH102",
        "title": "Calculus II",
        "description": "Techniques of integration, series, sequences, and introduction to multivariable calculus.",
        "credits": 4,
        "dept": "MATH",
        "level": "undergraduate",
        "prereqs": ["MATH101"],
        "tags": ["calculus", "series", "integration techniques", "multivariable", "mathematics"],
        "syllabus_text": "Integration by parts, trigonometric substitution, partial fractions. Improper integrals. Sequences and series: convergence tests. Power series and Taylor series. Parametric equations and polar coordinates. Introduction to vectors and 3D geometry.",
    },
    {
        "code": "MATH201",
        "title": "Linear Algebra",
        "description": "Vectors, matrices, linear transformations, eigenvalues, and applications in data science.",
        "credits": 3,
        "dept": "MATH",
        "level": "undergraduate",
        "prereqs": ["MATH101"],
        "tags": ["linear algebra", "matrices", "eigenvalues", "vectors", "transformations"],
        "syllabus_text": "Vectors and vector spaces. Matrix operations and determinants. Systems of linear equations and Gaussian elimination. Linear transformations. Eigenvalues and eigenvectors. Diagonalisation. Orthogonality and least squares. Singular value decomposition. Applications to data science.",
    },
    {
        "code": "MATH202",
        "title": "Discrete Mathematics",
        "description": "Logic, sets, combinatorics, graph theory, and proof techniques essential for computer science.",
        "credits": 3,
        "dept": "MATH",
        "level": "undergraduate",
        "tags": ["discrete math", "logic", "combinatorics", "graph theory", "proofs"],
        "syllabus_text": "Propositional and predicate logic. Set theory and relations. Functions and cardinality. Mathematical induction. Combinatorics: permutations and combinations. Probability basics. Graph theory: trees and paths. Algorithms on graphs. Number theory and modular arithmetic.",
    },
    {
        "code": "MATH301",
        "title": "Probability Theory",
        "description": "Rigorous treatment of probability spaces, random variables, distributions, and limit theorems.",
        "credits": 3,
        "dept": "MATH",
        "level": "undergraduate",
        "prereqs": ["MATH102"],
        "tags": ["probability", "random variables", "distributions", "statistics", "mathematics"],
        "syllabus_text": "Probability spaces and axioms. Conditional probability and independence. Discrete random variables: Bernoulli, Binomial, Poisson. Continuous random variables: Normal, Exponential. Joint distributions. Expectation and variance. Law of large numbers. Central limit theorem.",
    },
    {
        "code": "MATH302",
        "title": "Multivariable Calculus",
        "description": "Partial derivatives, multiple integrals, vector fields, and theorems of Green, Stokes, and Gauss.",
        "credits": 4,
        "dept": "MATH",
        "level": "undergraduate",
        "prereqs": ["MATH102", "MATH201"],
        "tags": ["calculus", "multivariable", "vector calculus", "partial derivatives", "mathematics"],
        "syllabus_text": "Functions of several variables. Partial derivatives and gradient. Directional derivatives and tangent planes. Optimisation with Lagrange multipliers. Double and triple integrals. Change of variables. Line integrals. Green's theorem. Surface integrals. Stokes' and Divergence theorems.",
    },
    {
        "code": "MATH401",
        "title": "Numerical Methods",
        "description": "Computational techniques for solving mathematical problems: root finding, interpolation, ODEs.",
        "credits": 3,
        "dept": "MATH",
        "level": "undergraduate",
        "prereqs": ["MATH201", "CS101"],
        "tags": ["numerical methods", "computation", "approximation", "scientific computing", "python"],
        "syllabus_text": "Floating point arithmetic and errors. Root finding: bisection, Newton-Raphson. Linear system solvers: LU decomposition. Interpolation and splines. Numerical integration: trapezoidal and Simpson rules. ODE solvers: Euler and Runge-Kutta. Eigenvalue computation. Python with NumPy and SciPy.",
    },
    {
        "code": "MATH402",
        "title": "Graph Theory",
        "description": "Advanced graph theory: coloring, flows, matchings, planar graphs, and algorithmic applications.",
        "credits": 3,
        "dept": "MATH",
        "level": "graduate",
        "prereqs": ["MATH202"],
        "tags": ["graph theory", "algorithms", "combinatorics", "network analysis", "mathematics"],
        "syllabus_text": "Graph fundamentals: paths, cycles, connectivity. Trees and spanning trees. Euler and Hamiltonian paths. Graph coloring and chromatic number. Planar graphs and Kuratowski's theorem. Network flows: max-flow min-cut. Matchings in bipartite graphs. Spectral graph theory.",
    },

    # ── Data Science ─────────────────────────────────────────────────
    {
        "code": "DS101",
        "title": "Introduction to Data Science",
        "description": "Overview of the data science workflow: collection, cleaning, exploration, modelling, and communication.",
        "credits": 3,
        "dept": "DS",
        "level": "undergraduate",
        "tags": ["data science", "python", "pandas", "visualization", "eda"],
        "syllabus_text": "Data science lifecycle. Python for data science: NumPy and Pandas. Data cleaning and wrangling. Exploratory data analysis. Data visualisation with Matplotlib and Seaborn. Introduction to statistical modelling. Communicating results. Ethics in data science.",
    },
    {
        "code": "DS201",
        "title": "Data Wrangling and Visualisation",
        "description": "Advanced data manipulation, transformation pipelines, and storytelling with data visualisations.",
        "credits": 3,
        "dept": "DS",
        "level": "undergraduate",
        "prereqs": ["DS101"],
        "tags": ["data wrangling", "visualization", "pandas", "plotly", "tableau", "eda"],
        "syllabus_text": "Advanced Pandas: merge, reshape, and groupby. Handling missing data and outliers. Regular expressions for text data. Time series data. Interactive visualisations with Plotly. Dashboards with Streamlit. Geospatial data. Storytelling with data principles.",
    },
    {
        "code": "DS301",
        "title": "Big Data Technologies",
        "description": "Distributed computing with Spark, Hadoop, and streaming data processing pipelines.",
        "credits": 4,
        "dept": "DS",
        "level": "undergraduate",
        "prereqs": ["DS201", "CS301"],
        "tags": ["big data", "spark", "hadoop", "kafka", "distributed computing"],
        "syllabus_text": "Distributed computing concepts. Hadoop ecosystem: HDFS and MapReduce. Apache Spark: RDDs, DataFrames, and Spark SQL. Stream processing with Kafka and Spark Streaming. Data lakes and lakehouses. Delta Lake. Cloud big data: AWS EMR and Databricks.",
    },
    {
        "code": "DS401",
        "title": "Feature Engineering",
        "description": "Techniques for transforming raw data into features that improve machine learning model performance.",
        "credits": 3,
        "dept": "DS",
        "level": "graduate",
        "prereqs": ["DS201", "CS501"],
        "tags": ["feature engineering", "machine learning", "data preprocessing", "dimensionality reduction"],
        "syllabus_text": "Feature selection methods: filter, wrapper, embedded. Feature extraction: PCA and autoencoders. Encoding categorical variables. Handling imbalanced datasets. Text and image featurisation. Time-series features. Automated feature engineering. Feature stores.",
    },
    {
        "code": "DS402",
        "title": "Recommender Systems",
        "description": "Collaborative filtering, content-based filtering, and hybrid recommendation algorithms.",
        "credits": 4,
        "dept": "DS",
        "level": "graduate",
        "prereqs": ["CS501", "STAT301"],
        "tags": ["recommender systems", "collaborative filtering", "content-based", "matrix factorization", "hybrid"],
        "syllabus_text": "Introduction to recommendation. Collaborative filtering: user-based and item-based. Matrix factorisation: SVD and ALS. Content-based filtering and TF-IDF. Hybrid approaches. Deep learning for recommendations: neural collaborative filtering. Evaluation metrics: RMSE, precision, recall, NDCG. Cold-start problem.",
    },
    {
        "code": "DS403",
        "title": "Time Series Analysis",
        "description": "Forecasting techniques: ARIMA, exponential smoothing, and deep learning approaches for temporal data.",
        "credits": 3,
        "dept": "DS",
        "level": "graduate",
        "prereqs": ["STAT201", "DS201"],
        "tags": ["time series", "forecasting", "arima", "lstm", "seasonality"],
        "syllabus_text": "Time series components: trend, seasonality, noise. Stationarity and unit root tests. ARMA and ARIMA models. Seasonal decomposition. Exponential smoothing methods. VAR models for multivariate series. LSTM for time series. Prophet library. Evaluation: MAE, RMSE.",
    },
    {
        "code": "DS404",
        "title": "Data Engineering",
        "description": "Building robust ETL pipelines, data warehouses, and orchestrating workflows at scale.",
        "credits": 4,
        "dept": "DS",
        "level": "graduate",
        "prereqs": ["DS301", "CS301"],
        "tags": ["data engineering", "etl", "airflow", "data warehouse", "pipeline"],
        "syllabus_text": "ETL vs ELT paradigms. Data warehouse design: star and snowflake schemas. Apache Airflow for workflow orchestration. dbt for data transformation. Data quality and testing. Cloud data warehouses: BigQuery and Redshift. Data governance and lineage. Real-time pipelines.",
    },

    # ── Statistics ───────────────────────────────────────────────────
    {
        "code": "STAT101",
        "title": "Introductory Statistics",
        "description": "Descriptive statistics, probability, inference, and hypothesis testing for beginners.",
        "credits": 3,
        "dept": "STAT",
        "level": "undergraduate",
        "tags": ["statistics", "probability", "hypothesis testing", "data analysis", "beginner"],
        "syllabus_text": "Data types and visualisation. Measures of centre and spread. Probability rules. Binomial and normal distributions. Sampling distributions. Confidence intervals. Hypothesis testing: z-test and t-test. Chi-square tests. Correlation and simple regression.",
    },
    {
        "code": "STAT201",
        "title": "Statistical Inference",
        "description": "Estimation theory, hypothesis testing, likelihood, and Bayesian inference.",
        "credits": 3,
        "dept": "STAT",
        "level": "undergraduate",
        "prereqs": ["STAT101", "MATH301"],
        "tags": ["statistical inference", "hypothesis testing", "bayesian", "likelihood", "estimation"],
        "syllabus_text": "Point estimation: MLE and method of moments. Confidence intervals and pivotal quantities. Neyman-Pearson hypothesis testing. Power and sample size. Likelihood ratio tests. Introduction to Bayesian inference. Prior and posterior distributions. Credible intervals.",
    },
    {
        "code": "STAT301",
        "title": "Regression Analysis",
        "description": "Simple and multiple linear regression, model diagnostics, logistic regression, and GLMs.",
        "credits": 3,
        "dept": "STAT",
        "level": "undergraduate",
        "prereqs": ["STAT201", "MATH201"],
        "tags": ["regression", "linear models", "logistic regression", "statistics", "modelling"],
        "syllabus_text": "Simple linear regression and OLS. Multiple regression and multicollinearity. Model selection: AIC and BIC. Diagnostics: residuals and influence. Polynomial and interaction terms. Logistic regression. Generalised linear models: Poisson and Gamma. Mixed effects models.",
    },
    {
        "code": "STAT302",
        "title": "Bayesian Statistics",
        "description": "Bayesian modelling, MCMC sampling, hierarchical models, and probabilistic programming.",
        "credits": 3,
        "dept": "STAT",
        "level": "graduate",
        "prereqs": ["STAT201"],
        "tags": ["bayesian statistics", "mcmc", "probabilistic programming", "pymc", "hierarchical models"],
        "syllabus_text": "Bayes' theorem and prior selection. Conjugate families. Markov Chain Monte Carlo: Metropolis-Hastings and Gibbs sampling. Hamiltonian Monte Carlo. Hierarchical Bayesian models. Model comparison with WAIC. Probabilistic programming with PyMC. Bayesian regression.",
    },
    {
        "code": "STAT401",
        "title": "Experimental Design",
        "description": "Designing experiments, ANOVA, factorial designs, and A/B testing for data-driven decisions.",
        "credits": 3,
        "dept": "STAT",
        "level": "graduate",
        "prereqs": ["STAT301"],
        "tags": ["experimental design", "anova", "a/b testing", "factorial design", "statistics"],
        "syllabus_text": "Principles of experimental design. Completely randomised design. One-way and two-way ANOVA. Factorial and fractional factorial designs. Blocking and Latin squares. Response surface methodology. A/B testing and sequential testing. Power analysis. Non-parametric alternatives.",
    },

    # ── Electrical Engineering ───────────────────────────────────────
    {
        "code": "EE101",
        "title": "Circuit Analysis",
        "description": "DC/AC circuit fundamentals: Ohm's law, Kirchhoff's laws, and network analysis techniques.",
        "credits": 4,
        "dept": "EE",
        "level": "undergraduate",
        "tags": ["circuits", "electronics", "electrical engineering", "ohm's law", "analysis"],
        "syllabus_text": "Basic circuit elements: resistors, capacitors, inductors. Ohm's and Kirchhoff's laws. Node and mesh analysis. Thevenin and Norton equivalents. AC circuits and phasors. Power in AC circuits. Frequency response. Laplace transform methods.",
    },
    {
        "code": "EE201",
        "title": "Digital Electronics",
        "description": "Boolean algebra, logic gates, combinational and sequential circuits, and FPGA design.",
        "credits": 3,
        "dept": "EE",
        "level": "undergraduate",
        "prereqs": ["EE101"],
        "tags": ["digital electronics", "logic gates", "fpga", "verilog", "boolean algebra"],
        "syllabus_text": "Boolean algebra and logic minimisation. Combinational circuits: adders, multiplexers, decoders. Sequential circuits: flip-flops and registers. Finite state machines. Memory elements. Programmable logic: FPGAs. Hardware description with Verilog. Timing analysis.",
    },
    {
        "code": "EE301",
        "title": "Signal Processing",
        "description": "Continuous and discrete signals, Fourier analysis, filtering, and applications in communications.",
        "credits": 4,
        "dept": "EE",
        "level": "undergraduate",
        "prereqs": ["EE101", "MATH302"],
        "tags": ["signal processing", "fourier", "filtering", "dsp", "communications"],
        "syllabus_text": "Continuous and discrete-time signals. Fourier series and Fourier transform. Sampling theorem and aliasing. Z-transform. FIR and IIR filter design. FFT algorithms. Power spectral density. Applications: audio processing and communications. MATLAB/Python implementation.",
    },
    {
        "code": "EE401",
        "title": "Embedded Systems",
        "description": "Microcontroller programming, real-time operating systems, sensors, and IoT applications.",
        "credits": 4,
        "dept": "EE",
        "level": "undergraduate",
        "prereqs": ["EE201", "CS101"],
        "tags": ["embedded systems", "microcontroller", "iot", "rtos", "arduino", "raspberry pi"],
        "syllabus_text": "Microcontroller architecture: ARM Cortex-M. Assembly and C programming for embedded systems. Timers, interrupts, and GPIO. Serial protocols: UART, SPI, I2C. ADC and DAC. RTOS concepts: tasks and scheduling. Sensor interfacing. IoT protocols: MQTT and HTTP.",
    },
    {
        "code": "EE501",
        "title": "Machine Learning for Engineers",
        "description": "ML techniques applied to engineering problems: signal classification, fault detection, and control.",
        "credits": 3,
        "dept": "EE",
        "level": "graduate",
        "prereqs": ["EE301", "CS501"],
        "tags": ["machine learning", "engineering", "signal classification", "neural networks", "control systems"],
        "syllabus_text": "Feature extraction from signals. Classification for fault detection. Regression for system identification. Time series prediction with LSTMs. Reinforcement learning for control. Edge ML deployment on microcontrollers. TensorFlow Lite. Case studies: predictive maintenance.",
    },

    # ── Business ─────────────────────────────────────────────────────
    {
        "code": "BUS101",
        "title": "Business Analytics",
        "description": "Using data and statistical tools to drive business decisions, with Excel and Python.",
        "credits": 3,
        "dept": "BUS",
        "level": "undergraduate",
        "tags": ["business analytics", "data analysis", "decision making", "excel", "python"],
        "syllabus_text": "Business intelligence fundamentals. Descriptive analytics with Excel. Data-driven decision making. KPIs and dashboards. Predictive analytics basics. Customer segmentation. A/B testing for business. Reporting with Power BI. Case studies in retail and finance.",
    },
    {
        "code": "BUS201",
        "title": "Financial Modelling",
        "description": "Building financial models in Excel and Python for valuation, forecasting, and risk analysis.",
        "credits": 3,
        "dept": "BUS",
        "level": "undergraduate",
        "prereqs": ["BUS101"],
        "tags": ["finance", "financial modelling", "excel", "valuation", "risk"],
        "syllabus_text": "Time value of money. DCF valuation. Three-statement financial models. Scenario and sensitivity analysis. Monte Carlo simulation. Option pricing: Black-Scholes. Portfolio optimisation with Python. Risk metrics: VaR. Leveraged buyout modelling.",
    },
    {
        "code": "BUS301",
        "title": "Digital Marketing Analytics",
        "description": "Measuring and optimising digital marketing campaigns using analytics and attribution models.",
        "credits": 3,
        "dept": "BUS",
        "level": "undergraduate",
        "prereqs": ["BUS101"],
        "tags": ["marketing analytics", "digital marketing", "seo", "google analytics", "attribution"],
        "syllabus_text": "Digital marketing channels: SEO, SEM, social, email. Web analytics with Google Analytics 4. Attribution modelling. Customer lifetime value. Cohort analysis. Email A/B testing. Social media metrics. Marketing mix modelling. Campaign optimisation.",
    },
    {
        "code": "BUS401",
        "title": "Data-Driven Product Management",
        "description": "Product strategy, user research, experiment design, and metrics for modern product teams.",
        "credits": 3,
        "dept": "BUS",
        "level": "graduate",
        "prereqs": ["BUS101", "STAT101"],
        "tags": ["product management", "product strategy", "user research", "metrics", "experimentation"],
        "syllabus_text": "Product lifecycle and strategy. User research methods. Defining and measuring success metrics. Experiment design and A/B testing. Feature prioritisation frameworks: RICE and MoSCoW. Roadmap planning. Working with engineering teams. Case studies: Spotify and Airbnb.",
    },

    # ── Psychology ───────────────────────────────────────────────────
    {
        "code": "PSY101",
        "title": "Introduction to Psychology",
        "description": "Survey of major psychological theories, research methods, and applications to everyday life.",
        "credits": 3,
        "dept": "PSY",
        "level": "undergraduate",
        "tags": ["psychology", "behaviour", "cognition", "mental health", "research methods"],
        "syllabus_text": "History and approaches in psychology. Biological bases of behaviour. Sensation and perception. States of consciousness. Learning and conditioning. Memory and cognition. Language and thought. Motivation and emotion. Developmental psychology. Social psychology. Psychological disorders.",
    },
    {
        "code": "PSY201",
        "title": "Cognitive Psychology",
        "description": "Mental processes underlying perception, attention, memory, language, and problem solving.",
        "credits": 3,
        "dept": "PSY",
        "level": "undergraduate",
        "prereqs": ["PSY101"],
        "tags": ["cognitive psychology", "memory", "attention", "perception", "problem solving"],
        "syllabus_text": "Information processing models. Attention and dual-task performance. Short-term and working memory. Long-term memory: encoding and retrieval. Forgetting and memory distortions. Mental imagery. Language comprehension and production. Decision making and heuristics. Problem solving and creativity.",
    },
    {
        "code": "PSY301",
        "title": "Human-Computer Interaction",
        "description": "UX principles, usability testing, cognitive models, and designing user-centred systems.",
        "credits": 3,
        "dept": "PSY",
        "level": "undergraduate",
        "prereqs": ["PSY101"],
        "tags": ["hci", "ux design", "usability", "user research", "cognitive ergonomics"],
        "syllabus_text": "History of HCI. Human factors and cognitive ergonomics. Mental models and affordances. User-centred design process. Prototyping: low and high fidelity. Usability testing methods. Heuristic evaluation. Accessibility standards. Emotional design. Mobile and voice interfaces.",
    },
    {
        "code": "PSY401",
        "title": "Behavioural Economics",
        "description": "How cognitive biases and psychological factors influence economic decisions and policy design.",
        "credits": 3,
        "dept": "PSY",
        "level": "graduate",
        "prereqs": ["PSY201"],
        "tags": ["behavioural economics", "cognitive biases", "decision making", "nudge theory", "psychology"],
        "syllabus_text": "Rational vs. behavioural models. Prospect theory and loss aversion. Heuristics and biases: availability, anchoring, framing. Intertemporal choice and hyperbolic discounting. Social preferences and fairness. Nudge theory and choice architecture. Applications: savings, health, and policy.",
    },

    # ── Physics ──────────────────────────────────────────────────────
    {
        "code": "PHY101",
        "title": "Classical Mechanics",
        "description": "Newton's laws, kinematics, work-energy theorem, momentum, and rotational motion.",
        "credits": 4,
        "dept": "PHY",
        "level": "undergraduate",
        "prereqs": ["MATH101"],
        "tags": ["physics", "mechanics", "kinematics", "energy", "dynamics"],
        "syllabus_text": "Kinematics in 1D and 2D. Newton's laws of motion. Work, energy, and power. Conservation of energy and momentum. Rotational kinematics and dynamics. Torque and angular momentum. Oscillations and simple harmonic motion. Gravitation. Fluid statics and dynamics.",
    },
    {
        "code": "PHY201",
        "title": "Electromagnetism",
        "description": "Electric fields, magnetic fields, Maxwell's equations, and electromagnetic waves.",
        "credits": 4,
        "dept": "PHY",
        "level": "undergraduate",
        "prereqs": ["PHY101", "MATH302"],
        "tags": ["physics", "electromagnetism", "maxwell equations", "waves", "fields"],
        "syllabus_text": "Coulomb's law and electric field. Gauss's law. Electric potential. Capacitance. Current and resistance. Magnetic force and field. Ampere's law. Faraday's law and inductance. Maxwell's equations. Electromagnetic waves and the spectrum. Optics fundamentals.",
    },
    {
        "code": "PHY301",
        "title": "Quantum Mechanics",
        "description": "Wave-particle duality, Schrödinger equation, quantum states, and the principles of quantum physics.",
        "credits": 4,
        "dept": "PHY",
        "level": "graduate",
        "prereqs": ["PHY201", "MATH302"],
        "tags": ["quantum mechanics", "physics", "wave function", "uncertainty principle", "quantum computing"],
        "syllabus_text": "Historical background: photoelectric effect and Bohr model. Wave-particle duality and de Broglie. Schrödinger equation. Infinite and finite potential wells. Quantum harmonic oscillator. Operators and observables. Uncertainty principle. Spin and angular momentum. Multi-particle systems.",
    },
    {
        "code": "PHY401",
        "title": "Computational Physics",
        "description": "Numerical simulation of physical systems using Python: ODEs, Monte Carlo, and molecular dynamics.",
        "credits": 3,
        "dept": "PHY",
        "level": "graduate",
        "prereqs": ["PHY201", "MATH401"],
        "tags": ["computational physics", "simulation", "python", "monte carlo", "numerical methods"],
        "syllabus_text": "Python for scientific computing. Numerical ODE solving: RK4. Random number generation and Monte Carlo integration. Monte Carlo simulation of statistical mechanics. Molecular dynamics. Finite difference methods for PDEs. Fourier analysis in physics. Visualisation of physical systems.",
    },

    # ── Cross-disciplinary / Advanced ────────────────────────────────
    {
        "code": "DS501",
        "title": "MLOps and Model Deployment",
        "description": "Taking ML models to production: tracking, serving, monitoring, and CI/CD for ML systems.",
        "credits": 3,
        "dept": "DS",
        "level": "graduate",
        "prereqs": ["CS501", "CS505"],
        "tags": ["mlops", "model deployment", "mlflow", "docker", "monitoring", "production ml"],
        "syllabus_text": "ML lifecycle and technical debt. Experiment tracking with MLflow. Model registry and versioning. Model serving: REST APIs and batch. Docker and Kubernetes for ML. Feature stores. Data drift and model monitoring. CI/CD pipelines for ML. A/B testing in production.",
    },
    {
        "code": "CS507",
        "title": "Reinforcement Learning",
        "description": "Markov decision processes, Q-learning, policy gradient methods, and deep RL applications.",
        "credits": 4,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["CS501", "MATH301"],
        "tags": ["reinforcement learning", "mdp", "q-learning", "policy gradient", "deep rl"],
        "syllabus_text": "Markov decision processes. Dynamic programming: policy and value iteration. Monte Carlo methods. Temporal difference learning: Q-learning and SARSA. Function approximation with neural networks. Policy gradient: REINFORCE. Actor-critic methods. Proximal policy optimisation. Applications: games and robotics.",
    },
    {
        "code": "DS502",
        "title": "Ethics in AI and Data Science",
        "description": "Fairness, accountability, transparency, bias, privacy, and the societal impact of AI systems.",
        "credits": 2,
        "dept": "DS",
        "level": "graduate",
        "tags": ["ai ethics", "fairness", "bias", "privacy", "responsible ai", "data ethics"],
        "syllabus_text": "History of AI failures and harms. Bias sources: data, algorithm, deployment. Fairness metrics and trade-offs. Explainability and interpretability: LIME and SHAP. Privacy: differential privacy and federated learning. GDPR and regulatory landscape. Ethical frameworks for AI. Case studies.",
    },
    {
        "code": "CS508",
        "title": "Quantum Computing",
        "description": "Quantum bits, circuits, algorithms, and the future of quantum computational advantage.",
        "credits": 3,
        "dept": "CS",
        "level": "graduate",
        "prereqs": ["MATH201", "PHY301"],
        "tags": ["quantum computing", "qubits", "quantum algorithms", "qiskit", "cryptography"],
        "syllabus_text": "Quantum bits and superposition. Quantum gates and circuits. Entanglement and Bell states. Quantum parallelism. Deutsch-Jozsa and Grover's algorithms. Shor's factoring algorithm. Quantum error correction. Quantum machine learning overview. Qiskit programming.",
    },
    {
        "code": "DS503",
        "title": "Knowledge Graphs and Semantic Web",
        "description": "Ontologies, RDF, SPARQL, knowledge graph embedding, and applications in search and AI.",
        "credits": 3,
        "dept": "DS",
        "level": "graduate",
        "prereqs": ["CS301", "CS402"],
        "tags": ["knowledge graphs", "ontologies", "rdf", "sparql", "semantic web", "graph neural networks"],
        "syllabus_text": "Graph data models. RDF and OWL ontologies. SPARQL querying. Knowledge graph construction and completion. Knowledge graph embeddings: TransE and RotatE. Graph neural networks for KGs. Applications: search engines and question answering. Wikidata and DBpedia.",
    },
]

MODULES = {
    "CS101": [
        {
            "title": "Getting Started with Python", "order": 1,
            "description": "Set up your environment and write your first programs.",
            "activities": [
                {"title": "Welcome to the Course", "type": "page", "order": 1, "duration": 5,
                 "content": "Welcome! In this course you will learn the fundamentals of programming using Python. No prior experience is required."},
                {"title": "Installing Python & VS Code", "type": "page", "order": 2, "duration": 10,
                 "content": "Download Python 3.11+ from python.org and install Visual Studio Code with the Python extension."},
                {"title": "Your First Python Program", "type": "assignment", "order": 3, "duration": 20,
                 "content": "Write a Python script that prints 'Hello, World!' and your name. Submit the .py file."},
                {"title": "Python Basics Quiz", "type": "quiz", "order": 4, "duration": 10,
                 "content": "Quiz covering variables, print(), and basic syntax."},
            ],
        },
        {
            "title": "Control Flow", "order": 2,
            "description": "Conditionals, loops, and program logic.",
            "activities": [
                {"title": "If / Elif / Else", "type": "page", "order": 1, "duration": 15,
                 "content": "Conditional statements let your program make decisions. Learn if, elif, and else syntax with real examples."},
                {"title": "For and While Loops", "type": "page", "order": 2, "duration": 15,
                 "content": "Iteration is core to programming. Master for loops over sequences and while loops with conditions."},
                {"title": "FizzBuzz Challenge", "type": "assignment", "order": 3, "duration": 30,
                 "content": "Print numbers 1-100. For multiples of 3 print 'Fizz', multiples of 5 print 'Buzz', both print 'FizzBuzz'."},
                {"title": "Control Flow Quiz", "type": "quiz", "order": 4, "duration": 10,
                 "content": "Test your understanding of conditionals and loops."},
            ],
        },
        {
            "title": "Functions and Data Structures", "order": 3,
            "description": "Writing reusable code with functions and working with lists and dictionaries.",
            "activities": [
                {"title": "Defining and Calling Functions", "type": "page", "order": 1, "duration": 20,
                 "content": "Functions are reusable blocks of code. Learn def, parameters, return values, and scope."},
                {"title": "Lists and Tuples", "type": "page", "order": 2, "duration": 15,
                 "content": "Lists are ordered, mutable sequences. Tuples are immutable. Learn indexing, slicing, and common methods."},
                {"title": "Dictionaries", "type": "page", "order": 3, "duration": 15,
                 "content": "Dictionaries store key-value pairs. Learn creation, access, iteration, and common patterns."},
                {"title": "Python Docs - Built-in Types", "type": "url", "order": 4,
                 "url": "https://docs.python.org/3/library/stdtypes.html", "duration": None},
                {"title": "Shopping Cart Assignment", "type": "assignment", "order": 5, "duration": 45,
                 "content": "Build a simple shopping cart using a list of dictionaries. Support add, remove, and total functions."},
            ],
        },
    ],
    "CS501": [
        {
            "title": "Foundations of Machine Learning", "order": 1,
            "description": "Core concepts, the ML workflow, and your first models.",
            "activities": [
                {"title": "What is Machine Learning?", "type": "page", "order": 1, "duration": 10,
                 "content": "Machine learning is the study of algorithms that improve through experience. Overview of supervised, unsupervised, and reinforcement learning."},
                {"title": "The ML Workflow", "type": "page", "order": 2, "duration": 15,
                 "content": "Data collection → preprocessing → feature engineering → model selection → training → evaluation → deployment. Each step matters."},
                {"title": "scikit-learn Introduction", "type": "url", "order": 3,
                 "url": "https://scikit-learn.org/stable/getting_started.html", "duration": 20},
                {"title": "Module Quiz: ML Basics", "type": "quiz", "order": 4, "duration": 15,
                 "content": "Test understanding of ML terminology, bias-variance tradeoff, and the train/test split."},
            ],
        },
        {
            "title": "Supervised Learning", "order": 2,
            "description": "Linear models, decision trees, SVMs, and ensemble methods.",
            "activities": [
                {"title": "Linear & Logistic Regression", "type": "page", "order": 1, "duration": 30,
                 "content": "Linear regression for continuous targets. Logistic regression for binary classification. Gradient descent optimization."},
                {"title": "Decision Trees & Random Forests", "type": "page", "order": 2, "duration": 25,
                 "content": "Decision trees partition data by feature thresholds. Random forests aggregate many trees to reduce variance."},
                {"title": "Support Vector Machines", "type": "page", "order": 3, "duration": 20,
                 "content": "SVMs find the maximum-margin hyperplane. Kernel trick enables non-linear classification."},
                {"title": "Titanic Survival Prediction", "type": "assignment", "order": 4, "duration": 120,
                 "content": "Use the Titanic dataset to build a classifier. Try at least 3 algorithms, compare accuracy, and submit a Jupyter notebook."},
                {"title": "Supervised Learning Quiz", "type": "quiz", "order": 5, "duration": 20,
                 "content": "Questions on model selection, overfitting, regularisation, and cross-validation."},
            ],
        },
        {
            "title": "Unsupervised Learning & Evaluation", "order": 3,
            "description": "Clustering, dimensionality reduction, and model evaluation metrics.",
            "activities": [
                {"title": "K-Means & Hierarchical Clustering", "type": "page", "order": 1, "duration": 25,
                 "content": "K-means assigns points to nearest centroid iteratively. Hierarchical clustering builds a dendrogram bottom-up or top-down."},
                {"title": "PCA for Dimensionality Reduction", "type": "page", "order": 2, "duration": 20,
                 "content": "Principal Component Analysis finds orthogonal directions of maximum variance. Use it to visualise high-dimensional data."},
                {"title": "Evaluation Metrics Deep Dive", "type": "page", "order": 3, "duration": 20,
                 "content": "Accuracy, precision, recall, F1, ROC-AUC for classification. MSE, RMSE, MAE for regression. When to use each."},
                {"title": "Customer Segmentation Project", "type": "assignment", "order": 4, "duration": 90,
                 "content": "Apply k-means and hierarchical clustering to a retail dataset. Visualise clusters with PCA and interpret the segments."},
            ],
        },
    ],
    "DS101": [
        {
            "title": "Python for Data Science", "order": 1,
            "description": "NumPy, Pandas, and the data science toolkit.",
            "activities": [
                {"title": "NumPy Arrays", "type": "page", "order": 1, "duration": 20,
                 "content": "NumPy provides fast multi-dimensional arrays. Learn array creation, indexing, broadcasting, and vectorised operations."},
                {"title": "Pandas DataFrames", "type": "page", "order": 2, "duration": 25,
                 "content": "Pandas is the backbone of data manipulation. Master Series, DataFrame, loc/iloc, groupby, and merge."},
                {"title": "NumPy Documentation", "type": "url", "order": 3,
                 "url": "https://numpy.org/doc/stable/user/quickstart.html", "duration": 15},
                {"title": "Pandas Documentation", "type": "url", "order": 4,
                 "url": "https://pandas.pydata.org/docs/getting_started/10min.html", "duration": 15},
                {"title": "Data Wrangling Exercise", "type": "assignment", "order": 5, "duration": 60,
                 "content": "Given a messy CSV dataset, clean it using Pandas: handle missing values, fix data types, rename columns, and export a clean version."},
            ],
        },
        {
            "title": "Exploratory Data Analysis", "order": 2,
            "description": "Understanding data through statistics and visualisation.",
            "activities": [
                {"title": "Descriptive Statistics", "type": "page", "order": 1, "duration": 20,
                 "content": "Summarise data with mean, median, mode, variance, skewness. Use .describe() and understand distributions."},
                {"title": "Data Visualisation with Matplotlib", "type": "page", "order": 2, "duration": 25,
                 "content": "Create histograms, scatter plots, box plots, and line charts. Customise titles, labels, colours, and figure size."},
                {"title": "Advanced Plots with Seaborn", "type": "page", "order": 3, "duration": 20,
                 "content": "Seaborn builds on Matplotlib. Use pairplots, heatmaps, violin plots, and categorical plots with one line of code."},
                {"title": "EDA Quiz", "type": "quiz", "order": 4, "duration": 15,
                 "content": "Questions on choosing the right chart type, interpreting distributions, and identifying outliers."},
                {"title": "EDA Report Assignment", "type": "assignment", "order": 5, "duration": 90,
                 "content": "Choose a public dataset and perform full EDA. Write a short report with 5+ visualisations and key statistical insights."},
            ],
        },
    ],
    "MATH201": [
        {
            "title": "Vectors and Matrices", "order": 1,
            "description": "The building blocks of linear algebra.",
            "activities": [
                {"title": "Vectors in R^n", "type": "page", "order": 1, "duration": 20,
                 "content": "A vector is an ordered list of numbers. Learn addition, scalar multiplication, dot product, and geometric interpretation."},
                {"title": "Matrix Operations", "type": "page", "order": 2, "duration": 25,
                 "content": "Matrices represent linear transformations. Learn addition, multiplication, transpose, and the identity matrix."},
                {"title": "3Blue1Brown: Essence of Linear Algebra", "type": "url", "order": 3,
                 "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "duration": 60},
                {"title": "Vectors & Matrices Quiz", "type": "quiz", "order": 4, "duration": 20,
                 "content": "Test your understanding of vector operations, matrix multiplication rules, and dimensions."},
            ],
        },
        {
            "title": "Systems of Equations & Determinants", "order": 2,
            "description": "Solving linear systems and computing determinants.",
            "activities": [
                {"title": "Gaussian Elimination", "type": "page", "order": 1, "duration": 30,
                 "content": "Row reduction brings a matrix to row echelon form. Use it to solve Ax=b systematically."},
                {"title": "Determinants", "type": "page", "order": 2, "duration": 20,
                 "content": "The determinant of a square matrix encodes geometric scaling. Learn cofactor expansion and properties."},
                {"title": "System Solving Assignment", "type": "assignment", "order": 3, "duration": 60,
                 "content": "Solve 5 systems of linear equations using Gaussian elimination by hand, then verify with NumPy."},
                {"title": "Linear Systems Quiz", "type": "quiz", "order": 4, "duration": 15,
                 "content": "Questions on row reduction, rank, null space, and solution existence."},
            ],
        },
        {
            "title": "Eigenvalues and Applications", "order": 3,
            "description": "Eigendecomposition, PCA, and PageRank.",
            "activities": [
                {"title": "Eigenvalues and Eigenvectors", "type": "page", "order": 1, "duration": 25,
                 "content": "Av = λv defines eigenvectors. Learn the characteristic polynomial, how to compute eigenvalues, and geometric meaning."},
                {"title": "Diagonalisation", "type": "page", "order": 2, "duration": 20,
                 "content": "A diagonalisable matrix A = PDP^{-1} where D is diagonal. This simplifies matrix powers and exponentials."},
                {"title": "Application: PCA", "type": "page", "order": 3, "duration": 20,
                 "content": "PCA uses the eigenvectors of the covariance matrix to find principal components. Implement it with NumPy."},
                {"title": "Eigenvalues Quiz", "type": "quiz", "order": 4, "duration": 20,
                 "content": "Compute eigenvalues, verify eigenvectors, and determine diagonalisability."},
                {"title": "Spectral Analysis Project", "type": "assignment", "order": 5, "duration": 90,
                 "content": "Apply eigendecomposition to a real-world network (e.g. social graph). Compute the PageRank vector and interpret results."},
            ],
        },
    ],
    "STAT101": [
        {
            "title": "Descriptive Statistics", "order": 1,
            "description": "Summarising and visualising data.",
            "activities": [
                {"title": "Types of Data", "type": "page", "order": 1, "duration": 10,
                 "content": "Categorical vs numerical. Nominal, ordinal, interval, ratio scales. Choosing the right analysis depends on data type."},
                {"title": "Measures of Centre and Spread", "type": "page", "order": 2, "duration": 20,
                 "content": "Mean, median, mode. Variance, standard deviation, IQR, range. When to use each and how outliers affect them."},
                {"title": "Charts and Graphs", "type": "page", "order": 3, "duration": 15,
                 "content": "Histograms, box plots, bar charts, and scatter plots. Match the chart to the data type and the question."},
                {"title": "Descriptive Stats Quiz", "type": "quiz", "order": 4, "duration": 15,
                 "content": "Calculate mean, median, variance, and choose appropriate visualisations for given datasets."},
            ],
        },
        {
            "title": "Probability and Distributions", "order": 2,
            "description": "The language of uncertainty.",
            "activities": [
                {"title": "Probability Rules", "type": "page", "order": 1, "duration": 20,
                 "content": "Sample spaces, events, union, intersection, complement. Addition and multiplication rules. Conditional probability."},
                {"title": "Discrete Distributions", "type": "page", "order": 2, "duration": 20,
                 "content": "Bernoulli, Binomial, Poisson distributions. PMF, CDF, expected value, variance. Real-world examples."},
                {"title": "The Normal Distribution", "type": "page", "order": 3, "duration": 20,
                 "content": "Bell curve, 68-95-99.7 rule, Z-scores, standardisation. Central limit theorem and why it matters."},
                {"title": "Probability Quiz", "type": "quiz", "order": 4, "duration": 20,
                 "content": "Calculate probabilities, identify distributions, apply the CLT."},
                {"title": "Simulation Assignment", "type": "assignment", "order": 5, "duration": 60,
                 "content": "Use Python to simulate 10,000 coin flips and dice rolls. Plot the distributions and compare to theoretical values."},
            ],
        },
        {
            "title": "Hypothesis Testing", "order": 3,
            "description": "Making decisions from data.",
            "activities": [
                {"title": "Hypothesis Testing Framework", "type": "page", "order": 1, "duration": 20,
                 "content": "Null and alternative hypotheses. Type I and Type II errors. p-values and significance levels. Power of a test."},
                {"title": "Z-test and T-test", "type": "page", "order": 2, "duration": 25,
                 "content": "One-sample and two-sample tests. When to use z vs t. Assumptions, test statistic, and interpretation."},
                {"title": "Khan Academy: Significance Tests", "type": "url", "order": 3,
                 "url": "https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample", "duration": 30},
                {"title": "Hypothesis Testing Quiz", "type": "quiz", "order": 4, "duration": 20,
                 "content": "Formulate hypotheses, choose the right test, interpret p-values, and state conclusions."},
                {"title": "A/B Test Analysis", "type": "assignment", "order": 5, "duration": 75,
                 "content": "Given results from an A/B test on two website designs, perform a two-sample t-test. State your conclusions with confidence intervals."},
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Seed the database with departments and courses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing courses and departments before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Course.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write("Cleared existing data.")

        # Create departments
        dept_map = {}
        for d in DEPARTMENTS:
            obj, created = Department.objects.get_or_create(code=d["code"], defaults={"name": d["name"]})
            dept_map[d["code"]] = obj
            if created:
                self.stdout.write(f"  Created department: {obj}")

        # Create courses (without prerequisites first)
        course_map = {}
        for c in COURSES:
            dept = dept_map.get(c["dept"])
            obj, created = Course.objects.get_or_create(
                code=c["code"],
                defaults={
                    "title": c["title"],
                    "description": c["description"],
                    "credits": c["credits"],
                    "department": dept,
                    "level": c["level"],
                    "tags": c.get("tags", []),
                    "syllabus_text": c.get("syllabus_text", ""),
                    "is_active": True,
                },
            )
            course_map[c["code"]] = obj
            if created:
                self.stdout.write(f"  Created course: {obj}")

        # Set prerequisites
        for c in COURSES:
            prereq_codes = c.get("prereqs", [])
            if prereq_codes:
                course_obj = course_map[c["code"]]
                prereqs = [course_map[p] for p in prereq_codes if p in course_map]
                course_obj.prerequisites.set(prereqs)

        # Seed modules and activities for representative courses
        module_count = 0
        activity_count = 0
        for course_code, module_list in MODULES.items():
            course_obj = course_map.get(course_code)
            if not course_obj:
                self.stdout.write(self.style.WARNING(f"  Course {course_code} not found, skipping modules."))
                continue

            for module_data in module_list:
                module_obj, module_created = CourseModule.objects.get_or_create(
                    course=course_obj,
                    title=module_data["title"],
                    defaults={
                        "description": module_data.get("description", ""),
                        "order": module_data["order"],
                    },
                )
                if module_created:
                    module_count += 1
                    self.stdout.write(f"    Created module: {module_obj}")

                # Clear existing activities for this module and recreate
                module_obj.activities.all().delete()

                activities_to_create = []
                for act in module_data.get("activities", []):
                    activities_to_create.append(
                        CourseActivity(
                            module=module_obj,
                            title=act["title"],
                            activity_type=act["type"],
                            content=act.get("content", ""),
                            url=act.get("url", ""),
                            order=act["order"],
                            duration_minutes=act.get("duration"),
                        )
                    )
                created_activities = CourseActivity.objects.bulk_create(activities_to_create)
                activity_count += len(created_activities)

        total = Course.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {total} courses and {Department.objects.count()} departments in the database."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Modules seeded: {module_count}. Activities seeded: {activity_count}."
        ))
