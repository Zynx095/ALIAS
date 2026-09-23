import { AlertProvider } from './context/AlertContext';
import MainLayout from './layouts/MainLayout';
import Overview from './pages/Overview';
import InvestigationWorkspace from './pages/InvestigationWorkspace';
import InvestigationHistory from './pages/InvestigationHistory';
import LoginPortal from './pages/LoginPortal';
import { useViewState } from './hooks/useViewState';

export default function App() {
  const [view, navigate] = useViewState();

  const goOverview = () => navigate({ name: 'overview' });
  const goHistory = () => navigate({ name: 'history' });
  const goPortal = () => navigate({ name: 'portal' });

  // `from` is an in-memory hint for the Back button
  const openInvestigation = (eventId, from = 'overview') => navigate({ name: 'investigation', eventId, from });
  const goBackFromInvestigation = () => (view.from === 'history' ? goHistory() : view.from === 'portal' ? goPortal() : goOverview());

  // Maps MainLayout's nav ids ('dashboard' / 'investigations' / 'portal') onto real surfaces
  const navActiveId = view.name === 'history' ? 'investigations' : view.name === 'overview' ? 'dashboard' : view.name === 'portal' ? 'portal' : null;
  const handleNavSelect = (id) => {
    if (id === 'investigations') goHistory();
    else if (id === 'portal') goPortal();
    else goOverview();
  };

  const title = view.name === 'investigation'
    ? 'Forensic Investigation'
    : view.name === 'history'
    ? 'Investigation Register'
    : view.name === 'portal'
    ? 'Yukith Hub · Login Portal'
    : 'SOC Workspace';

  const viewKey = view.name === 'investigation' ? `investigation-${view.eventId}` : view.name;

  return (
    <AlertProvider>
      <MainLayout activeView={navActiveId} setView={handleNavSelect} title={title} viewKey={viewKey}>
        {view.name === 'overview' && <Overview onOpenInvestigation={openInvestigation} />}
        {view.name === 'investigation' && (
          <InvestigationWorkspace eventId={view.eventId} onBack={goBackFromInvestigation} origin={view.from} />
        )}
        {view.name === 'history' && (
          <InvestigationHistory onOpenInvestigation={(eventId) => openInvestigation(eventId, 'history')} />
        )}
        {view.name === 'portal' && (
          <LoginPortal onOpenInvestigation={(id) => openInvestigation(id, 'portal')} onGoOverview={goOverview} />
        )}
      </MainLayout>
    </AlertProvider>
  );
}
