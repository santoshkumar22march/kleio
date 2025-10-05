import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

const SettingsPage = () => {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleConnect = async () => {
    if (code.length !== 6) {
      toast({
        title: 'Invalid Code',
        description: 'Please enter the 6-character code from the Telegram bot.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.post('/api/users/verify-telegram', { verification_code: code });
      if (response.data.success) {
        toast({
          title: 'Account Connected!',
          description: 'Your Telegram account has been successfully linked.',
        });
        setCode('');
      } else {
        throw new Error(response.data.detail || 'An unknown error occurred.');
      }
    } catch (error: any) {
      toast({
        title: 'Connection Failed',
        description: error.response?.data?.detail || error.message || 'Failed to link account. Please try again.',
        variant: 'destructive',
      });
    }
    setIsLoading(false);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Connect Telegram</CardTitle>
          <CardDescription>
            Enter the verification code from the Kleio.ai Telegram bot to link your account.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="XXXXXX"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            maxLength={6}
          />
          <Button onClick={handleConnect} disabled={isLoading} className="w-full">
            {isLoading ? 'Connecting...' : 'Connect Account'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPage;
