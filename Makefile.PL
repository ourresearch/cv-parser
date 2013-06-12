use strict;
use warnings;

use ExtUtils::MakeMaker;

WriteMakefile(
  NAME         => 'app.pl',
  VERSION      => '1.0',
  AUTHOR       => 'Marc <marrrcandre@gmail.com>',
  EXE_FILES    => ['app.pl'],
  PREREQ_PM    => {'Mojolicious' => '2.0',
                    'Class::Struct',
                    'Getopt::Long',
                    'Getopt::Std',
                    'File::Basename',
                    'File::Spec',
                    'FindBin',
                    'HTML::Entities',
                    'IO::File',
                    'POSIX',
                    'XML::Parser',
                    'XML::Twig',
                    'XML::Writer',
                    'XML::Writer::String'},
  test         => {TESTS => 't/*.t'}
);
