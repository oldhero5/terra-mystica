import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MapPin, Upload, Zap, Shield } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="glass-dark border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MapPin className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold gradient-text">Terra Mystica</h1>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">
              How it Works
            </a>
            <Button variant="outline" size="sm">
              Sign In
            </Button>
            <Button className="btn-aurora" size="sm">
              Get Started
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex items-center justify-center py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-6xl font-bold mb-6 gradient-text animate-float">
              Discover the World
            </h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Upload any outdoor image and our AI will pinpoint its location within 50 meters. 
              Experience the future of geolocation technology.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="btn-aurora px-8 py-6 text-lg">
                <Upload className="mr-2 h-5 w-5" />
                Upload Image
              </Button>
              <Button variant="outline" size="lg" className="px-8 py-6 text-lg">
                View Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <h3 className="text-4xl font-bold text-center mb-12 gradient-text">
            Powerful Features
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="card-hover glass-dark">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Get results in under 3 seconds with our optimized AI pipeline
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="card-hover glass-dark">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/20 rounded-lg flex items-center justify-center mb-4">
                  <MapPin className="h-6 w-6 text-secondary" />
                </div>
                <CardTitle>50m Accuracy</CardTitle>
                <CardDescription>
                  Pinpoint locations with incredible precision using advanced ML models
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="card-hover glass-dark">
              <CardHeader>
                <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-accent" />
                </div>
                <CardTitle>Secure & Private</CardTitle>
                <CardDescription>
                  Your images are processed securely and never stored permanently
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4">
          <h3 className="text-4xl font-bold text-center mb-12 gradient-text">
            How It Works
          </h3>
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-primary">1</span>
                </div>
                <h4 className="text-xl font-semibold mb-2">Upload Image</h4>
                <p className="text-muted-foreground">
                  Drag and drop or select your outdoor image
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-secondary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-secondary">2</span>
                </div>
                <h4 className="text-xl font-semibold mb-2">AI Analysis</h4>
                <p className="text-muted-foreground">
                  Our models analyze visual features and terrain
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-accent">3</span>
                </div>
                <h4 className="text-xl font-semibold mb-2">Get Location</h4>
                <p className="text-muted-foreground">
                  Receive precise coordinates and confidence score
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="glass-dark border-t">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MapPin className="h-6 w-6 text-primary" />
              <span className="font-semibold">Terra Mystica</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2024 Terra Mystica. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}