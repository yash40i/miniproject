# Resume-Insight AI - Frontend

Next.js React application for the Resume-Insight AI platform. Provides a modern UI for resume analysis, skill matching, and learning path generation.

## 🚀 Quick Start

### Prerequisites
- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Backend Connection

By default, the frontend connects to the backend at `http://localhost:8000`.

To change the API endpoint, edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://your-api-url:8000
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Homepage with resume upload form
│   ├── results/[id]/      # Dynamic results page
│   ├── layout.tsx         # Root layout
│   ├── providers.tsx      # React context providers
│   └── globals.css        # Global Tailwind styles
├── lib/
│   ├── api.ts             # API client for backend communication
│   └── store.ts           # Zustand stores for state management
├── components/            # Reusable React components (future)
├── public/                # Static assets
└── package.json           # Dependencies and scripts
```

## 🔧 Key Libraries

- **Next.js 15**: React framework for production
- **React 18**: UI library
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Zustand**: Lightweight state management
- **React Query**: Server state management (optional)
- **React Toastify**: Toast notifications
- **Lucide React**: Icon library
- **Recharts**: Chart visualization (future)

## 📄 Main Pages

### Home Page (`/`)
- Resume file upload (drag & drop or click to browse)
- Job description textarea
- Semantic matching analysis trigger
- Feature highlights

### Results Page (`/results/[id]`)
- Overall match score and metrics
- Tabbed interface:
  - **Overview**: Gap analysis and recommendations
  - **Skills**: Matched skills with similarity scores and missing skills
  - **Learning Path**: Structured milestones with timelines and resources

## 🔌 API Integration

The frontend communicates with the FastAPI backend via REST endpoints:

- `POST /api/analyze` - Upload resume and job description
- `GET /api/results/{analysis_id}` - Fetch analysis results
- `DELETE /api/results/{analysis_id}` - Delete analysis
- `GET /api/stats` - Get API statistics
- `GET /health` - Health check

### Response Example

```typescript
{
  analysis_id: "uuid-string",
  status: "completed",
  matching_result: {
    overall_score: 75.5,
    matched_skills: [...],
    missing_skills: [...]
  },
  feedback: {
    gap_analysis: "...",
    recommendations: [...]
  },
  learning_path: {
    title: "...",
    milestones: [...]
  }
}
```

## 🎨 UI Features

- **Dark Theme**: Slate-based color scheme optimized for readability
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Drag & Drop**: Resume file upload with visual feedback
- **Real-time Status**: Loading states and progress indicators
- **Toast Notifications**: User feedback for actions and errors
- **Gradient Accents**: Blue and purple gradients for visual hierarchy

## 📦 Build & Deploy

```bash
# Production build
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint
```

## 🔐 Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API base URL (default: http://localhost:8000)

## 🛠️ Development

### Hot Reload
Development server supports hot module replacement (HMR) for instant UI updates.

### Debug Mode
Enable debug output by setting `DEBUG=resume-insight:*` in your environment.

## 📝 Type Definitions

All API responses are typed using TypeScript interfaces in `lib/api.ts`:
- `AnalysisResult`
- `MatchingResult`
- `SkillMatch`
- `FeedbackResult`
- `LearningPath`
- `Milestone`

## 🚀 Performance Optimizations

- Code splitting via Next.js dynamic imports
- Image optimization (if images added)
- CSS optimization with Tailwind purging
- API response caching with React Query (optional)

## 🤝 State Management

Using Zustand for lightweight global state:
- `useAnalysisStore`: Analysis state (ID, results, loading)
- `useUIStore`: UI state (sidebar, theme)

## 📚 Future Enhancements

- [ ] Export results as PDF
- [ ] Share analysis results via link
- [ ] Dark/Light theme toggle
- [ ] Multi-language support
- [ ] Advanced filtering and sorting
- [ ] Result comparison tool
- [ ] User authentication and history
- [ ] Resume builder integration

## 🐛 Troubleshooting

### Connection refused error
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled on backend

### Build errors
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (requires v18+)

## 📞 Support

For issues or questions, refer to the main project README or contact the development team.

## 📄 License

MIT License - See LICENSE file in root directory
