# IELTS GenAI Prep Platform

A complete AI-powered IELTS test preparation platform with mobile-first in-app purchases and QR code cross-platform authentication.

## Overview

IELTS GenAI Prep is an innovative AI-powered platform for IELTS test preparation that offers assessment services for Academic and General Training IELTS. The platform leverages a serverless AWS Lambda architecture and utilizes AI for comprehensive evaluation across all IELTS criteria.

### Key Features

- **TrueScore® Writing Assessment**: Advanced AI evaluation for both Academic and General Training writing tasks
- **ClearScore® Speaking Assessment**: Maya AI examiner provides authentic speaking assessment with real-time analysis
- **Cross-Platform Access**: Mobile app purchases with seamless web platform access via QR code authentication
- **Official Band-Aligned Feedback**: Detailed feedback aligned with official IELTS band descriptors

## System Architecture

### Backend Infrastructure
- **Pure AWS Lambda Serverless architecture**
- **Multi-region deployment** across `us-east-1`, `eu-west-1`, and `ap-southeast-1`
- **API Gateway** for regional endpoints and automatic routing
- **WebSocket API** for real-time bi-directional communication

### Frontend Architecture
- **Progressive Web App (PWA)** optimized for mobile and desktop
- **Capacitor-based native iOS/Android mobile applications**
- **QR Code Authentication** for seamless transitions between mobile and web

### AI Services Integration
- **Amazon Nova Sonic** for bi-directional speech-to-speech conversations with AI examiner Maya
- **Amazon Nova Micro** for text processing and assessment evaluation
- **Real-time streaming** via WebSockets for speaking assessments

## Payment Integration

### Mobile-Only Purchase Model
```
Payment Integration:
├── Apple App Store (iOS in-app purchases) - $36.49 per assessment package
├── Google Play Store (Android in-app purchases) - $36.49 per assessment package
└── QR Code Authentication (Web access after mobile purchase)
```

**Important Notes:**
- **NO web-based payments** - all purchases must be made through mobile app stores
- **NO Stripe integration** - exclusively mobile app store transactions
- **Assessment packages** include 4 complete practice tests per purchase
- **Cross-platform access** via QR code after mobile purchase

### Assessment Products Available
- **Academic Speaking Assessment** - IELTS Academic Speaking test with AI examiner Maya
- **Academic Writing Assessment** - IELTS Academic Writing Tasks 1 & 2 with TrueScore® feedback
- **General Training Speaking Assessment** - IELTS General Training Speaking test
- **General Training Writing Assessment** - IELTS General Training Writing Tasks 1 & 2

## Authentication Flow

### QR Code Cross-Platform Authentication
1. **Mobile Purchase**: User purchases assessment in mobile app ($36.49)
2. **Receipt Validation**: App Store/Google Play receipt verification
3. **QR Generation**: Mobile app generates QR code for web access
4. **Web Authentication**: User scans QR code to access assessments on web
5. **Session Management**: 1-hour web session with full assessment access

## Technical Implementation

### Data Flow
- **Purchase-to-Assessment**: Mobile app purchase → receipt validation → web platform access via QR
- **Speech Assessment**: Web initiation → WebSocket connection → Nova Sonic streaming → real-time feedback
- **Multi-Region**: DynamoDB Global Tables for cross-region data replication
- **Data Storage**: AWS DynamoDB replaces PostgreSQL for serverless architecture

### Deployment Strategy
- **Multi-Region Serverless Deployment**
- **Mobile App Distribution** via Apple App Store and Google Play Store
- **Production Website**: www.ieltsaiprep.com with TrueScore® and ClearScore® branding

## Development

### Local Development
```bash
# Install dependencies
npm install

# Start development server
python main.py
# or
gunicorn --bind 0.0.0.0:5000 main:app
```

### Environment Variables
- `AWS_REGION`: AWS region for DynamoDB (default: us-east-1)
- `SESSION_SECRET`: Flask session secret key
- `RECAPTCHA_V2_SITE_KEY`: Google reCAPTCHA site key
- `RECAPTCHA_V2_SECRET_KEY`: Google reCAPTCHA secret key
- `JWT_SECRET`: JWT token secret for mobile authentication
- `KMS_KEY_ID`: AWS KMS key for encryption

## Security

- **CloudFront-based blocking** with custom header validation
- **Google reCAPTCHA v2** integration for secure authentication
- **AWS SES** email confirmation system
- **Environment variables** for all sensitive configuration

## Mobile App Features

### iOS/Android Applications
- **In-app purchases** at $36.49 per assessment product
- **Receipt validation** with Apple App Store and Google Play Store
- **QR code generation** for web platform access
- **Native platform features** via Capacitor
- **Regional API routing** for optimal performance

### Capacitor Integration
- **Cross-platform compatibility** for iOS and Android
- **Native device access** for enhanced mobile experience
- **Automated build pipeline** for app store deployment

## Production Deployment

### Live Website
- **URL**: https://www.ieltsaiprep.com
- **CDN**: CloudFront distribution
- **SSL**: AWS Certificate Manager
- **DNS**: Route 53 management

### AWS Lambda Infrastructure
- **Function**: `ielts-genai-prep-api`
- **Runtime**: Python 3.11
- **Memory**: 512MB
- **Timeout**: 30 seconds
- **Regions**: Multi-region deployment

## License

This project is proprietary software owned by Worldwide Publishing Company of America (WWPCA).

## Support

For technical support and inquiries, please contact the development team through the official channels.