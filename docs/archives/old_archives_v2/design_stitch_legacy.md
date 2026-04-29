# Stitch Design Specification

## # tokens
- primary: #8cc63f
- secondary: #1e293b
- surface: #f8fafc

## # components
### Button[cta]
- Text: "S'inscrire"
- Action: Redirect to register

### Form[login]
- Fields: email, password
- Button: "Se connecter"
- Intent: POST /api/auth/login

### Card[stats]
- Icon: trend-up
- Data: users_count, revenue
- Intent: GET /api/stats/dashboard

## # layout
- Grid: 12 cols
- Breakpoints: 640px, 1024px
