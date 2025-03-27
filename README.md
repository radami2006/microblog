# 🚀 MicroBlog: A Modern Social Platform

[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-4479A1?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)

## 🧑‍💻 About Me

As a first year telecommunications engineering student at Universidad Pontificia Comillas (ICAI) with a passion for software development and cybersecurity, I've built this project to demonstrate my technical capabilities and security-conscious approach to web development.

My professional interests lie at the intersection of secure application development, network architecture, and data protection. This project showcases not only my ability to build feature-rich web applications but also my commitment to implementing security best practices throughout the development lifecycle.

With a solid foundation in telecommunications fundamentals and growing knowledge in cybersecurity concepts, I bring a fresh perspective to software development that prioritizes both functionality and security. My technical skill set spans backend development, database design, authentication systems, and secure API implementation—all demonstrated in this MicroBlog platform.

## 💡 Project Overview

[Project Link]([radami2006.pythonanywhere.com](https://radami2006.pythonanywhere.com)

MicroBlog is a secure social networking application built with Flask, implementing industry-standard authentication practices and data protection measures. The platform demonstrates my ability to create scalable, maintainable, and secure web applications with modern architecture patterns.

### ✨ Key Technical Features

- **Secure Authentication System**:
  - Password hashing using Werkzeug's security functions
  - Protection against CSRF attacks
  - Session management with Flask-Login
  
- **Robust Database Architecture**:
  - Relational database design with SQLAlchemy ORM
  - Database migrations handling with Alembic
  - Data integrity constraints and validation
  
- **Advanced Web Security Implementations**:
  - Input validation and sanitization
  - Protection against XSS vulnerabilities
  - Secure file upload handling
  
- **Scalable Application Structure**:
  - Blueprint-based modular architecture
  - Separation of concerns design pattern
  - RESTful API principles

- **User Experience & Frontend Integration**:
  - Responsive design with Bootstrap
  - AJAX for dynamic content updates
  - Client-side form validation

## 🛠️ Technical Stack

- **Backend**: Flask, Python 3
- **Database**: SQLAlchemy ORM, SQLite (dev), PostgreSQL (production-ready)
- **Security**: Flask-Login, CSRF protection, secure password hashing
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript/AJAX
- **Infrastructure**: Compatible with cloud deployment (PythonAnywhere, Heroku, AWS)
- **Tools**: Git version control, Alembic migrations, virtual environments

## 🔐 Security Features

- Secure authentication with password hashing
- Protection against common web vulnerabilities (CSRF, XSS)
- Secure file upload handling with validation and sanitization
- User input validation and sanitization
- Session management best practices
- Authorization checks for protected resources

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
   ```
   git clone https://github.com/radami2006/microblog.git
   cd microblog
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables (create a .env file)
   ```
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=sqlite:///app.db
   ```

5. Initialize the database
   ```
   flask db upgrade
   ```

6. Run the development server
   ```
   flask run
   ```

## 🔍 Code Quality & Best Practices

- **Clean Architecture**: Separation of concerns with blueprints
- **Documentation**: Comprehensive docstrings and comments
- **Security First**: Implementation of OWASP security guidelines
- **Testing**: Support for unit and integration tests
- **Maintainability**: Consistent code style and organization

## 💼 Professional Applications

This project demonstrates my capability to:
- Develop secure authentication systems applicable to enterprise applications
- Implement proper database design patterns for scalable applications
- Create maintainable codebases using modern web development practices
- Balance technical requirements with user experience considerations
- Apply security principles throughout the development lifecycle

## 🔮 Future Enhancements

- OAuth 2.0 integration for third-party authentication
- Two-factor authentication
- End-to-end encryption for private messages
- Content delivery network (CDN) integration
- Advanced analytics and monitoring

## 📬 Contact

I'm currently exploring new professional opportunities in software development and cybersecurity. Feel free to connect with me:

- [GitHub](https://github.com/radami2006)
- [LinkedIn](https://www.linkedin.com/in/daniel-maestre-l%C3%B3pez-1a5287332/)
- Email: daniel.maestre.lopez@outlook.es

---

<p align="center">
  <i>Developed with a security-first mindset by a telecommunications engineering student with a great interest in secure software development.</i>
</p>
